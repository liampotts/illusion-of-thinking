from functools import partial

import gradio as gr
from ollama import Client

from puzzles import TowersOfHanoi, CheckerJumping, RiverCrossing, BlocksWorld


class OllamaClient:
    def __init__(self):
        self.model = ""
        self.client = Client()
        self.tools = []
        self.stream = True

        models = self.client.list()
        self.models = [model.model for model in models.models]

    def unload(self):
        self.client.generate(model=self.model, prompt=" ", keep_alive=0)

    def chat(self, model: str, messages: list[dict], options: dict):
        if self.model != model:
            if self.model != "":
                self.unload()
            self.model = model

        for response in self.client.chat(
            model=self.model,
            tools=self.tools,
            stream=self.stream,
            options=options,
            messages=messages,
        ):
            yield response.message.content


def solve(client, model, system, user, messages):
    prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    messages.append({"role": "assistant", "content": "Solving... "})
    yield messages

    for response in client.chat(model=model, messages=prompt, options={}):
        messages[-1]["content"] += response
        yield messages


def evaluate(puzzle, n, messages):
    task = puzzles[puzzle](n)
    solution = messages[-1]["content"]
    solved, result = task.evaluate(solution)
    messages.append({"role": "user", "content": result})
    return messages


if __name__ == "__main__":
    puzzles = {
        TowersOfHanoi.NAME: TowersOfHanoi,
        CheckerJumping.NAME: CheckerJumping,
        RiverCrossing.NAME: RiverCrossing,
        BlocksWorld.NAME: BlocksWorld,
    }
    client = OllamaClient()

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                bot = gr.Chatbot(type="messages", height=500)
                clear = gr.ClearButton([bot])
                model = gr.Dropdown(
                    label="Model",
                    choices=client.models,
                    value=client.models[0],
                )
                options = gr.TextArea(label="Options", value="{}", lines=4)
            with gr.Column():
                puzzle = gr.Dropdown(
                    label="Puzzle",
                    choices=list(puzzles.keys()),
                    value=TowersOfHanoi.NAME,
                )
                n = gr.Number(value=1, maximum=10, minimum=1, label="Difficulty")
                button = gr.Button("Solve")
                with gr.Tab("System"):
                    system = gr.TextArea(
                        label="System", value=TowersOfHanoi.SYSTEM_PROMPT, lines=22
                    )
                with gr.Tab("User"):
                    user = gr.TextArea(
                        label="User", value=TowersOfHanoi().user_prompt(), lines=22
                    )

        def setup(puzzle, n):
            task = puzzles[puzzle](n)
            return task.SYSTEM_PROMPT, task.user_prompt()

        puzzle.change(setup, inputs=[puzzle, n], outputs=[system, user])
        n.change(setup, inputs=[puzzle, n], outputs=[system, user])
        button.click(
            partial(solve, client), inputs=[model, system, user, bot], outputs=[bot]
        ).then(evaluate, inputs=[puzzle, n, bot], outputs=[bot])

    demo.launch()
