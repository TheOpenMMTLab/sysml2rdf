from sysml2rdf.parse_sysml_file import parse_comment
import pytest

def test_parse_comment_simple_id():
    assert parse_comment("{id xxx}") == {"id": "xxx"}

def test_parse_comment_simple_ref():
    assert parse_comment("{ref xxx}") == {"ref": ["xxx"]}

def test_parse_comment_simple_ref2():
    assert parse_comment("{ref xxx,yyy}") == {"ref": ["xxx","yyy"]}

def test_parse_comment_simple_ref2():
    assert parse_comment("{ref xxx,yyy} und {ref zzz:123}") == {"ref": ["xxx","yyy","zzz:123"]}

def test_parse_comment_simple_complex():
    assert parse_comment("{id xxx-27:a} und {ref zzz:123:gh-abc}") == {"ref": ["zzz:123:gh-abc"] , "id": "xxx-27:a"}

def test_parse_comment_simple_complex_text():

    text = " Die Schnittstelle {id IF:KME:2:QKD:2-ABC} erfüllt." 
    text += " die Anfroderungen {ref QKD:2, QKref-7, All:Req:Protokolle:Kompatibilität}"

    assert parse_comment(text) == {"ref": ["QKD:2","QKref-7","All:Req:Protokolle:Kompatibilität"] , "id": "IF:KME:2:QKD:2-ABC"}


def test_parse_comment_invalid_syntax1():
    with pytest.raises(ValueError):
        parse_comment("{id: xxx}")

def test_parse_comment_invalid_syntax2():
    with pytest.raises(ValueError):
        parse_comment("{ref xxx:345 yyy-123}")

def test_parse_comment_invalid_syntax3():
    with pytest.raises(ValueError):
        parse_comment("{ ref xxx:345, yyy-123}")

def test_parse_comment_invalid_syntax4():
    with pytest.raises(ValueError):
        parse_comment("{id xxx,yyy}")
