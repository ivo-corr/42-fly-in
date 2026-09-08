import sys
import unittest
from fly_in import parse_config, InputFileError

STRICT = "--strict" in sys.argv

class TestParsing(unittest.TestCase):
    def test_nb_drones_first_line(self):
        with self.assertRaises(Exception):
            with open("test_maps/01.txt") as file:
                parse_config(file.read())
    def test_negative_nb_drones(self):
        with self.assertRaises(Exception):
            with open("test_maps/02.txt") as file:
                parse_config(file.read())
    def test_duplicate_start_hub(self):
        with self.assertRaises(Exception):
            with open("test_maps/03.txt") as file:
                parse_config(file.read())
    def test_duplicate_end_hub(self):
        with self.assertRaises(Exception):
            with open("test_maps/04.txt") as file:
                parse_config(file.read())
    def test_duplicate_hub_name(self):
        with self.assertRaises(Exception):
            with open("test_maps/05.txt") as file:
                parse_config(file.read())
    def test_non_integer_coordinate(self):
        with self.assertRaises(Exception):
            with open("test_maps/06.txt") as file:
                parse_config(file.read())
    def test_dash_in_zone_name(self):
        with self.assertRaises(Exception):
            with open("test_maps/07.txt") as file:
                parse_config(file.read())
    def test_space_in_zone_name(self):
        with self.assertRaises(Exception):
            with open("test_maps/08.txt") as file:
                parse_config(file.read())
    def test_false_connection(self):
        with self.assertRaises(Exception):
            with open("test_maps/09.txt") as file:
                parse_config(file.read())
    def test_duplicate_connection_simple(self):
        with self.assertRaises(Exception):
            with open("test_maps/10.txt") as file:
                parse_config(file.read())
    def test_duplicate_connection_converse(self):
        with self.assertRaises(Exception):
            with open("test_maps/11.txt") as file:
                parse_config(file.read())
    def test_zone_metadata(self):
        with self.assertRaises(Exception):
            with open("test_maps/12.txt") as file:
                parse_config(file.read())
    def test_zone_metadata_02(self):
        with self.assertRaises(Exception):
            with open("test_maps/13.txt") as file:
                parse_config(file.read())
    def test_connection_metadata(self):
        with self.assertRaises(Exception):
            with open("test_maps/14.txt") as file:
                parse_config(file.read())

if __name__ == "__main__":
    if STRICT:
        sys.argv.remove("--strict")
    unittest.main()
