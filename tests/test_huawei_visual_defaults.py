import json
import unittest
from pathlib import Path


class HuaweiVisualDefaultsRegression(unittest.TestCase):
    def test_huawei_8_plus_4_models_use_neutral_factory_visual(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / 'src/devices/supported_devices.json').read_text(encoding='utf-8'))
        models = {str(item.get('model')): item for item in payload.get('devices', []) if isinstance(item, dict)}
        for model in ('S5720-12TP-LI-AC', 'S5735-L8P4X-A1'):
            device = models[model]
            self.assertEqual(device.get('calibration_profile'), 'stock_24rj45_4sfp')
            self.assertEqual(device.get('default_faceplate'), 'faceplates/24rj45-4sfp.png')
            visuals = device.get('visuals') or {}
            self.assertEqual(visuals.get('calibration_profile'), 'stock_24rj45_4sfp')
            self.assertEqual(visuals.get('recommended_faceplate'), 'faceplates/24rj45-4sfp.png')


if __name__ == '__main__':
    unittest.main()
