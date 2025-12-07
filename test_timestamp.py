import pandas as pd
import unittest


class TestTimestampProcessing( unittest.TestCase ):
    def test_timestamp_conversion_and_sort(self):
        # Création du DataFrame de test
        test_data = pd.DataFrame(
            {'col': ['24-11-2025 22:19:20', '25-11-2025 10:05:30', 'invalid', '23-11-2025 15:45:00']} )

        # Conversion en datetime
        test_data['col'] = pd.to_datetime( test_data['col'], format='%d-%m-%Y %H:%M:%S', errors='coerce' )

        # Assertion 1: Vérifie le type datetime
        self.assertTrue( pd.api.types.is_datetime64_any_dtype( test_data['col'] ),
                         "La colonne n'est pas de type datetime" )

        # Enlève les lignes invalides
        test_data = test_data[test_data['col'].notna()]

        # Extraction de l'heure
        test_data['col'] = test_data['col'].dt.strftime( '%H:%M:%S' )

        # Tri ascendant
        test_data = test_data.sort_values( by='col', ascending=True ).reset_index( drop=True )

        # Assertion 2: Vérifie le tri (ex: première valeur est la plus petite heure)
        self.assertEqual( test_data['col'].iloc[0], '10:05:30', "Le tri n'est pas correct" )

        # Affiche pour debug (optionnel)
        print( test_data )


if __name__ == "__main__":
    unittest.main()
    import pandas as pd
    print("Test: BANDAS imported successfully")