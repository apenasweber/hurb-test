import random

from locust import HttpUser, between, task

currency_codes = [
    "usd",
    "brl",
    "eur",
    "btc",
    "eth",
]


class CurrencyEndpoints(HttpUser):
    wait_time = between(0, 1)

    @task
    def get_all_currencies_prices(self):
        self.client.get("/currency")

    # @task
    # def create_fictitious_currency(self):
    #     self.client.post(
    #         "/currency",
    #         json={
    #             "currency_code": "FICT",
    #             "rate": 1,
    #             "backed_by": "USD",
    #         },
    #     )

    # @task
    # def read_fictitious_currency(self):
    #     self.client.get("/currency/FICT")

    # @task
    # def update_fictitious_currency(self):
    #     self.client.put(
    #         "/currency",
    #         json={
    #             "currency_code": "FICT",
    #             "rate": 1,
    #             "backed_by": "USD",
    #         },
    #     )

    # @task
    # def delete_fictitious_currency(self):
    #     self.client.delete("/currency/FICT")

    # @task
    # def get_specific_currency_with_currency_code(self):
    #     currency_code = random.choice(currency_codes)
    #     self.client.get(f"/currency/{currency_code}")


# class ConverterEndpoints(HttpUser):
#     wait_time = between(0, 1)

#     @task
#     def convert_currency(self):
#         self.client.get(
#             f"?from_this={random.choice(currency_codes)}&amount=1&to={random.choice(currency_codes)}"
#         )
