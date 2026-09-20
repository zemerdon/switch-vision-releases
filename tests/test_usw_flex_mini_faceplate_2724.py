from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"src"
sys.path.insert(0,str(SRC))
from faceplate_native_canvas import png_dimensions, render_space_calibration
PROFILE=SRC/"calibration"/"faceplate-usw-flex-mini.json"
PNG=SRC/"faceplates"/"usw-flex-mini.png"
REGISTRY=SRC/"devices"/"supported_devices.json"
EXPECTED={
"1":{"center":[444,288],"number":[444,373],"led_left":[392,243],"led_right":[495,243],"hitbox":[119,111]},
"2":{"center":[684,288],"number":[684,387],"led_left":[632,243],"led_right":[735,243],"hitbox":[119,111]},
"3":{"center":[924,288],"number":[924,373],"led_left":[872,243],"led_right":[975,243],"hitbox":[119,111]},
"4":{"center":[1164,288],"number":[1164,387],"led_left":[1112,243],"led_right":[1215,243],"hitbox":[119,111]},
"5":{"center":[1404,288],"number":[1404,373],"led_left":[1352,243],"led_right":[1455,243],"hitbox":[119,111]}}
class USWFlexMiniFaceplateContract(unittest.TestCase):
    def test_geometry_round_trip(self):
        d=json.loads(PROFILE.read_text())
        self.assertEqual(d["profile"],"usw_flex_mini")
        self.assertEqual(d["model"],"usw-flex-mini")
        self.assertEqual(d["image"]["coordinate_space"],"image-native-v1")
        self.assertEqual(png_dimensions(PNG),(d["image"]["width"],d["image"]["height"]))
        r=render_space_calibration(d)
        self.assertEqual(list(r["ports"]),["1","2","3","4","5"])
        for port,expected in EXPECTED.items():
            for key,value in expected.items(): self.assertEqual(r["ports"][port][key],value,(port,key))
            self.assertEqual(r["ports"][port].get("supported_speed") or "","")
            self.assertEqual(r["ports"][port].get("port_role") or "","")
        self.assertEqual(r["ui"]["port_status_output"],"status_box_2")
        self.assertEqual(r["ui"]["port_led_shape"],"rectangle")
        self.assertEqual(r["ui"]["port_number_color"],"#000000")
        self.assertEqual(r["ui"]["port_number_font_size"],30)
        hidden=set(r["ui"]["status_panel"]["hidden_fields"]["switch"])
        self.assertIn("temp",hidden)
        self.assertIn("poe",hidden)
    def test_dedicated_assignment_only(self):
        rows={x["model"]:x for x in json.loads(REGISTRY.read_text())["devices"] if isinstance(x,dict)}
        mini=rows["USW Flex Mini"]
        self.assertEqual(mini["ports"]["rj45"],5)
        self.assertEqual(mini["ports"]["uplinks"],0)
        self.assertEqual(mini["default_faceplate"],"faceplates/usw-flex-mini.png")
        self.assertEqual(mini["calibration_profile"],"usw_flex_mini")
        for model in ("USW Flex","USW Flex 2.5G 5","UCG Ultra"):
            self.assertNotEqual(rows[model]["default_faceplate"],mini["default_faceplate"])
            self.assertNotEqual(rows[model]["calibration_profile"],mini["calibration_profile"])
if __name__=="__main__": unittest.main()
