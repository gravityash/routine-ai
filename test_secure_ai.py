import unittest
import json
import os
import app as flask_app

class TestSecureAIIntegration(unittest.TestCase):
    def setUp(self):
        flask_app.app.config['TESTING'] = True
        flask_app.app.config['SECRET_KEY'] = 'test_secret'
        self.client = flask_app.app.test_client()
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        self.sample_data = {
            "age": 25,
            "gender": "Male",
            "weight": 70,
            "height": 175,
            "bmi": 22.9,
            "goal": "weight_loss",
            "sleep_hours": 5.5,
            "stress_level": 7,
            "steps_walked": 4500,
            "exercise_minutes": 15,
            "calories_intake": 2200,
            "protein_intake": 45,
            "water_intake": 1.5,
            "screen_time": 7,
            "work_hours": 8,
            "meditation_minutes": 0
        }

    def test_predict_endpoint_fallback_and_structure(self):
        # Test without GEMINI_API_KEY set (simulates fallback / key missing)
        os.environ.pop("GEMINI_API_KEY", None)
        response = self.client.post('/predict', json=self.sample_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("prediction", data)
        self.assertIn("ai_markdown", data)
        self.assertTrue(data.get("is_fallback"))
        self.assertIn("Root Causes & Health Assessment", data["ai_markdown"])
        # Ensure no raw API key or trace is exposed
        self.assertNotIn("AIza", data["ai_markdown"])

    def test_api_ai_root_cause_endpoint(self):
        os.environ.pop("GEMINI_API_KEY", None)
        response = self.client.post('/api/ai/root-cause', json={"userData": self.sample_data})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "fallback")
        self.assertTrue(data.get("is_fallback"))
        self.assertIn("ai_markdown", data)
        self.assertIn("root_cause_analysis", data)
        self.assertIn("AI analysis is temporarily unavailable", data["message"])
        self.assertNotIn("AIza", response.get_data(as_text=True))

    def test_with_invalid_api_key_resilience(self):
        # Set invalid dummy key
        os.environ["GEMINI_API_KEY"] = "invalid_dummy_test_key"
        response = self.client.post('/api/ai/root-cause', json={"userData": self.sample_data})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "fallback")
        self.assertTrue(data.get("is_fallback"))
        self.assertIn("ai_markdown", data)
        # Ensure the invalid key is never reflected back to the client
        self.assertNotIn("invalid_dummy_test_key", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()

