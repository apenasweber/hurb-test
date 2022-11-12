from fastapi.testclient import TestClient


def test_should_not_create_existing_currency_in_database(
    client: TestClient, real_currency_data_brl: dict
):
    res = client.post("/currency/", json=real_currency_data_brl)
    assert res.status_code == 409
    assert (
        res.json()["detail"]
        == f"Currency code {real_currency_data_brl['currency_code']} already exists"
    )


def test_should_create_currency_that_not_exists_in_database(
    client: TestClient, fictitious_currency_data_hurb: dict
):
    res = client.post("/currency/", json=fictitious_currency_data_hurb)
    print(res.json())
    res_data = res.json()["data"]

    assert res.status_code == 201
    assert res_data["currency_code"] == fictitious_currency_data_hurb["currency_code"]
    assert res_data["rate"] == fictitious_currency_data_hurb["rate"]
    assert res_data["backed_by"] == fictitious_currency_data_hurb["backed_by"]


def test_should_create_currency_with_alternative_body(
    client: TestClient, fictitious_currency_data_hurb_alternative_input
):
    payload = fictitious_currency_data_hurb_alternative_input
    res = client.post("/currency/", json=payload)
    res_data = res.json()["data"]

    assert res.status_code == 201
    assert res_data["currency_code"] == payload["currency_code"]
    assert res_data["rate"] == payload["amount"] / payload["backed_currency_amount"]
    assert res_data["backed_by"] == payload["backed_by"]


def test_should_not_create_currency_with_missing_fields_in_body(
    client: TestClient, fictitious_currency_data_hurb_missing_field_input: dict
):
    res = client.post(
        "/currency/", json=fictitious_currency_data_hurb_missing_field_input
    )

    assert res.status_code == 422
    assert (
        res.json()["detail"][0]["msg"]
        == "You should provide whether a rate field or an amount and backed_currency_amount fields"
    )


def test_should_not_create_currency_with_wrong_fields_in_body(
    client: TestClient, fictitious_currency_data_hurb_all_fields_input: dict
):
    res = client.post("/currency/", json=fictitious_currency_data_hurb_all_fields_input)

    assert res.status_code == 422
    assert (
        res.json()["detail"][0]["msg"]
        == "You should provide only a rate field or an amount and backed_currency_amount fields"
    )
