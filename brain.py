import ollama
import threading
from memory import get_cached, save_cache


class Brain:

    def __init__(self):

        self.model = "llama3.2:1b"
        self.mode = "fast"
        self.history = []

        self.system_prompt = """
You are CAI (Custom Artificial Intelligence).

You are fast, helpful, and strong at:
- coding
- reasoning
- problem solving
"""

        self.mode_settings = {
            "fast": {"num_predict": 40, "temperature": 0.6},
            "balanced": {"num_predict": 120, "temperature": 0.7},
            "coding": {"num_predict": 220, "temperature": 0.3},
            "thinking": {"num_predict": 400, "temperature": 0.8}
        }

        # preload model (removes first-response delay)
        threading.Thread(target=self.preload_model, daemon=True).start()

    # ---------------- PRELOAD ----------------

    def preload_model(self):

        try:
            ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": "hi"}],
                options={"num_predict": 1}
            )
        except:
            pass

    # ---------------- MODE ----------------

    def set_mode(self, mode):

        if mode in self.mode_settings:
            self.mode = mode

    # ---------------- MAIN PROCESS ----------------

    def process(self, message, callback=None, mode=None):

        if mode:
            self.set_mode(mode)

        cached = get_cached(message)

        if cached:
            if callback:
                callback(cached)
            return cached

        self.history.append({
            "role": "user",
            "content": message
        })

        if len(self.history) > 12:
            self.history = self.history[-12:]

        settings = self.mode_settings[self.mode]

        full_response = ""

        try:

            stream = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt}
                ] + self.history,
                stream=True,
                options={
                    "num_predict": settings["num_predict"],
                    "temperature": settings["temperature"],
                    "top_k": 20,
                    "num_ctx": 2048
                }
            )

            for chunk in stream:

                text = chunk["message"]["content"]

                full_response += text

                if callback:
                    callback(text)

        except Exception as e:

            error = f"⚠ Error: {e}"

            if callback:
                callback(error)

            return error

        self.history.append({
            "role": "assistant",
            "content": full_response
        })

        save_cache(message, full_response)

        return full_response