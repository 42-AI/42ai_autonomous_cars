
from get_data.src import utils_fct


def test_remove_label_to_delete():
    d_label = utils_fct.get_label_dict_from_file("test/resources/labels_delete.json")
    l_to_delete = utils_fct.remove_label_to_delete_from_dict(d_label)
    for _, label in d_label.items():
        assert "to_delete" not in label
    assert len(l_to_delete) == 2
    assert len(d_label) == 2


def test_remove_label_to_delete_nothing2delete():
    d_label = utils_fct.get_label_dict_from_file("test/resources/labels.json")
    l_to_delete = utils_fct.remove_label_to_delete_from_dict(d_label)
    for _, label in d_label.items():
        assert "to_delete" not in label
    assert len(l_to_delete) == 0
    assert len(d_label) == 4


def test_remove_label_to_delete_todelete_false():
    d_label = {
        "20200212T15-39-30-123456": {
            "to_delete": False,
            "img_id": "20200212T15-39-30-123456",
            "s3_bucket": "my-bucket",
            "label_fingerprint": "e170fca7848a59a815d2288802cc2832"
        },
        "20200212T15-39-30-987654": {
            "to_delete": True,
            "img_id": "20200212T15-39-30-987654",
            "s3_bucket": "my-bucket",
            "label_fingerprint": "e170fca7848a59a815d2288802aa1111"
        }
    }
    l_to_delete = utils_fct.remove_label_to_delete_from_dict(d_label)
    for _, label in d_label.items():
        assert "to_delete" not in label
    assert len(l_to_delete) == 1
    assert len(d_label) == 1


def test_get_label_fingerprint_all_different():
    d_label = utils_fct.get_label_dict_from_file("test/resources/labels.json")
    for img_id, label in d_label.items():
        fingerprint = utils_fct.get_label_finger_print(label)
        for img_id_bis, label_bis in d_label.items():
            if img_id == img_id_bis: continue
            assert fingerprint != utils_fct.get_label_finger_print(label_bis)


def test_get_label_fingerprint_invariant():
    d_label = utils_fct.get_label_dict_from_file("test/resources/labels.json")
    d_fingerprint = {}
    for img_id, label in d_label.items():
        d_fingerprint[img_id] = utils_fct.get_label_finger_print(label)
    for img_id, label in d_label.items():
        assert d_fingerprint[img_id] == utils_fct.get_label_finger_print(label)


def test_get_label_fingerprint_depends_on_imgid():
    d_label = utils_fct.get_label_dict_from_file("test/resources/labels.json")
    img_id, label = next(iter(d_label.items()))
    fingerprint = utils_fct.get_label_finger_print(label)
    label["img_id"] = img_id[1:]
    assert fingerprint != utils_fct.get_label_finger_print(label)
