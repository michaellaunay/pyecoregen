"""Generation contracts, including installed-wheel execution in qualification."""
import importlib
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pyecore import ecore
from pyecore.resources import ResourceSet, URI
from pyecoregen.adapter import pythonic_names
from pyecoregen.ecore import EcoreGenerator


def test_names_restored_on_error():
    original = ecore.ENamedElement.__getattribute__
    try:
        with pytest.raises(RuntimeError):
            with pythonic_names():
                raise RuntimeError('render failed')
        assert ecore.ENamedElement.__getattribute__ is original
    finally:
        ecore.ENamedElement.__getattribute__ = original


def test_escaped_literals_and_roundtrip(tmp_path, monkeypatch):
    package = ecore.EPackage('unicode_model', nsURI="urn:test:'\\é", nsPrefix='é')
    cls = ecore.EClass('Élément')
    package.eClassifiers.append(cls)
    attr = ecore.EAttribute('texte', ecore.EString, defaultValueLiteral="l'été\\\nligne")
    cls.eStructuralFeatures.append(attr)
    cls.eStructuralFeatures.append(ecore.EAttribute('count', ecore.EInt, defaultValueLiteral='42'))
    doc = ecore.EAnnotation('http://www.eclipse.org/emf/2002/GenModel')
    doc.details['documentation'] = 'Doc """ avec \\n et é'
    cls.eAnnotations.append(doc)
    model = tmp_path / 'entrée avec espaces ; $.ecore'
    rset = ResourceSet()
    resource = rset.create_resource(URI(str(model)))
    resource.append(package)
    resource.save()
    loaded = ResourceSet().get_resource(URI(str(model))).contents[0]
    out = tmp_path / "sortie ; $ ' é"
    EcoreGenerator().generate(loaded, str(out))
    for path in out.rglob('*.py'):
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    monkeypatch.syspath_prepend(str(out))
    mm = importlib.import_module(package.name)
    try:
        assert mm.nsURI == package.nsURI
        assert mm.Élément.__doc__ == doc.details['documentation']
        obj = mm.Élément()
        assert obj.texte == attr.defaultValueLiteral
        assert obj.count == 42
        # XML requires a valid namespace URI; escaping above is independent.
        mm.eClass.nsURI = mm.nsURI = 'urn:test:unicode'
        obj.texte = 'valeur é \\ "\n'
        for suffix in ('xmi', 'json'):
            rs = ResourceSet()
            rs.metamodel_registry[mm.nsURI] = mm
            target = tmp_path / ('instance.' + suffix)
            res = rs.create_resource(URI(str(target)))
            res.append(obj)
            res.save()
            rs2 = ResourceSet()
            rs2.metamodel_registry[mm.nsURI] = mm
            restored = rs2.get_resource(URI(str(target))).contents[0]
            assert isinstance(restored, mm.Élément)
            assert restored.texte == obj.texte
            assert restored.count == 42
    finally:
        for name in list(sys.modules):
            if name == package.name or name.startswith(package.name + '.'):
                del sys.modules[name]


def test_hash_seed_determinism(tmp_path):
    script = '''
from pyecore.ecore import EPackage, EClass, EReference, EAttribute, EEnum
from pyecoregen.ecore import EcoreGenerator
import sys
root = EPackage('root')
for name in ['zeta', 'alpha', 'beta']:
    p = EPackage(name)
    root.eSubpackages.append(p)
    for n in ['Z', 'A', 'B']:
        p.eClassifiers.append(EClass(n + name))
c = EClass('User')
root.eClassifiers.append(c)
for p in root.eSubpackages:
    for target in p.eClassifiers:
        c.eStructuralFeatures.append(EReference('ref' + target.name, target))
c.eSuperTypes.append(root.eSubpackages[0].eClassifiers[0])
kind = EEnum('Kind', literals=['A', 'B'])
root.eSubpackages[1].eClassifiers.append(kind)
c.eStructuralFeatures.append(EAttribute('kind', kind, defaultValueLiteral='B'))
generator = EcoreGenerator()
trace = []
for task in generator.tasks:
    run = task.run
    def traced(element, outfolder, run=run, task=task):
        trace.append(task.relative_path_for_element(element))
        return run(element, outfolder)
    task.run = traced
generator.generate(root, sys.argv[1])
import json
print(json.dumps(trace))
sys.path.insert(0, sys.argv[1])
import root
obj = root.User()
assert obj.kind is root.alpha.Kind.B

'''
    # Explicit installed module paths preserve qualification provenance, even for
    # editable snapshots; no implicit checkout/cwd import in the child.
    import pyecore, multigen, pyecoregen
    paths = [str(Path(m.__file__).resolve().parent.parent) for m in (pyecore, multigen, pyecoregen)]
    outputs = []
    traces = []
    for seed in ('1', '2', '77', '1'):
        folder = tmp_path / str(len(outputs))
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=os.pathsep.join(paths))
        process = subprocess.run([sys.executable, '-c', script, str(folder)], env=env,
                       cwd=tmp_path, check=True, capture_output=True, text=True)
        traces.append(process.stdout)
        for p in folder.rglob('*.py'):
            compile(p.read_text(encoding='utf-8'), str(p), 'exec')
        outputs.append({str(p.relative_to(folder)): p.read_bytes() for p in folder.rglob('*.py')})
    assert traces[0] and all(trace == traces[0] for trace in traces)
    assert outputs[0]
    assert all(output == outputs[0] for output in outputs)


@pytest.mark.parametrize('name', ['../escape', 'absolute', 'a/b', 'bad-name'])
def test_invalid_package_path_rejected_before_writing(tmp_path, name):
    if name == 'absolute':
        name = str(tmp_path / 'absolute')
    package = ecore.EPackage(name)
    with pytest.raises(ValueError, match='identifier'):
        EcoreGenerator().generate(package, str(tmp_path / 'out'))
    assert not (tmp_path / 'out').exists()


def test_cli_subprocess_and_generated_object(tmp_path):
    import pyecore, multigen, pyecoregen
    paths = [str(Path(m.__file__).resolve().parent.parent) for m in (pyecore, multigen, pyecoregen)]
    model = tmp_path / 'modèle ; $.ecore'
    package = ecore.EPackage('class', nsURI='urn:test:keyword', nsPrefix='kw')
    cls = ecore.EClass('pass')
    cls.eStructuralFeatures.append(ecore.EAttribute('else', ecore.EString))
    package.eClassifiers.append(cls)
    resource = ResourceSet().create_resource(URI(str(model)))
    resource.append(package)
    resource.save()
    output = tmp_path / 'output ; $ é'
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(paths))
    subprocess.run([sys.executable, '-m', 'pyecoregen.cli', '-e', str(model), '-o', str(output)],
                   env=env, cwd=tmp_path, check=True, capture_output=True, text=True)
    env['PYTHONPATH'] = os.pathsep.join([str(output), *paths])
    subprocess.run([sys.executable, '-c',
                    'from class_ import pass_; obj = pass_(else_="é"); assert obj.else_ == "é"'],
                   env=env, cwd=tmp_path, check=True, capture_output=True, text=True)


def test_nested_name_context_and_failed_generation(tmp_path):
    original = ecore.ENamedElement.__getattribute__
    p = ecore.EPackage('while')
    with pythonic_names():
        outer = ecore.ENamedElement.__getattribute__
        with pythonic_names():
            assert p.name == 'while_'
        assert ecore.ENamedElement.__getattribute__ is outer
    assert ecore.ENamedElement.__getattribute__ is original
    generator = EcoreGenerator()
    def fail(text):
        raise RuntimeError('formatter failed')
    generator.tasks[0].formatter = fail
    with pytest.raises(RuntimeError, match='formatter failed'):
        generator.generate(p, str(tmp_path))
    assert ecore.ENamedElement.__getattribute__ is original


def test_import_order_is_explicit():
    from pyecoregen.ecore import EcorePackageModuleTask, EcorePackageInitTask
    consumer = ecore.EPackage('consumer')
    cls = ecore.EClass('User')
    consumer.eClassifiers.append(cls)
    for pname in ('zeta', 'alpha'):
        provider = ecore.EPackage(pname)
        for cname in ('Z', 'A'):
            base = ecore.EClass(cname + pname)
            provider.eClassifiers.append(base)
            cls.eSuperTypes.append(base)
            cls.eStructuralFeatures.append(ecore.EReference('ref' + base.name, base))
    for mapping in (EcorePackageModuleTask.imported_classifiers(consumer),
                    EcorePackageInitTask.imported_classifiers_package(consumer)):
        assert [p.name for p in mapping] == ['alpha', 'zeta']
        assert [[c.name for c in values] for values in mapping.values()] == [
            ['Aalpha', 'Zalpha'], ['Azeta', 'Zzeta']]
