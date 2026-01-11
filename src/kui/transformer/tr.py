from kui.core.transformer import ProviderDataTransformer


class JSONTextResourceDataTransformer(ProviderDataTransformer):

    def nest(self, data: list[dict]):
        formatted_data = {}

        for record in sorted(data, key=lambda r: r.get("key")):
            key = record.get("key")
            locale = record.get("locale")
            value = record.get("text")

            translations = formatted_data.get(key, {})
            translations[locale] = value

            formatted_data[key] = translations

        return formatted_data

    def flatten(self, data: dict[str, dict[str, str]]):
        resources = []

        for resource_key, resource_data in data.items():
            for locale_id, resource_value in resource_data.items():

                resources.append({
                    "key": resource_key,
                    "locale": locale_id,
                    "text": resource_value
                })

        return resources
