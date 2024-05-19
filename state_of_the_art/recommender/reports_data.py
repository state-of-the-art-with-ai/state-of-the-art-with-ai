from state_of_the_art.config import config


class ReportsData:
    def get_summary(self):
        return config.get_datawarehouse().event("state_of_the_art_summary")

    def schema(self):
        return self.get_summary().dtypes

    def get_latest_summary(self, as_json=False, as_dict=False):
        result = self.get_summary().iloc[-1]
        if as_json:
            return result.to_json()
        if as_dict:
            return result.to_dict()

        return result["summary"]

    def get_latest_date_covered_by_summary(self):
        return (
            self.get_summary()
            .sort_values(by="to_date", ascending=False)
            .head(1)
            .to_dict()["to_date"][0]
        )
