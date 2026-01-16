from kui.core.transformer import ProviderDataTransformer


class JSONTextResourceDataTransformer(ProviderDataTransformer):
    """
    Transformer specifically for i18n text resources.
    Converts between flat translation records and nested locale dictionaries.
    """

    def nest(self, data: list[dict]):
        """
        Groups flat translation records into a nested dictionary keyed by resource name.

        Args:
            data (list[dict]): A list of records containing 'key', 'locale', and 'text'.

        Returns:
            dict: A nested dictionary where each key maps to a sub-dictionary of locales.
        """

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
        """
        Flattens a nested translation dictionary into a simple list of records.

        Args:
            data (dict): A nested dictionary of the form {key: {locale: text}}.

        Returns:
            list[dict]: A list of dictionaries ready for flat-file or database storage.
        """

        resources = []

        for resource_key, resource_data in data.items():
            for locale_id, resource_value in resource_data.items():

                resources.append({
                    "key": resource_key,
                    "locale": locale_id,
                    "text": resource_value
                })

        return resources
