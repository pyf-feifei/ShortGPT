import gradio as gr

from gui.content_automation_ui import GradioContentAutomationUI
from gui.ui_abstract_base import AbstractBaseUI
from gui.ui_components_html import GradioComponentsHTML
from gui.ui_tab_asset_library import AssetLibrary
from gui.ui_tab_config import ConfigUI
from shortGPT.utils.cli import CLI


def _patch_gradio_api_info():
    if getattr(gr.Blocks.get_api_info, "_shortgpt_safe", False):
        return

    original_get_api_info = gr.Blocks.get_api_info

    def safe_get_api_info(self, *args, **kwargs):
        try:
            return original_get_api_info(self, *args, **kwargs)
        except Exception as exc:
            print(f"Warning: falling back to empty Gradio API info: {exc}")
            return {"named_endpoints": {}, "unnamed_endpoints": {}}

    safe_get_api_info._shortgpt_safe = True
    gr.Blocks.get_api_info = safe_get_api_info


class ShortGptUI(AbstractBaseUI):
    '''Class for the GUI. This class is responsible for creating the UI and launching the server.'''

    def __init__(self, colab=False):
        super().__init__(ui_name='gradio_shortgpt')
        self.colab = colab
        CLI.display_header()

    def create_interface(self):
        '''Create Gradio interface'''
        with gr.Blocks(theme=gr.themes.Default(spacing_size=gr.themes.sizes.spacing_sm), css="footer {visibility: hidden}", title="ShortGPT Demo") as shortGptUI:
            with gr.Row(variant='compact'):
                gr.HTML(GradioComponentsHTML.get_html_header())

            self.content_automation = GradioContentAutomationUI(shortGptUI).create_ui()
            self.asset_library_ui = AssetLibrary().create_ui()
            self.config_ui = ConfigUI().create_ui()
        return shortGptUI

    def launch(self):
        '''Launch the server'''
        _patch_gradio_api_info()
        shortGptUI = self.create_interface()
        if not getattr(self, 'colab', False):
                    print("\n\n********************* STARTING SHORTGPT **********************")
                    print("\nShortGPT is running here 👉 http://localhost:31415\n")
                    print("********************* STARTING SHORTGPT **********************\n\n")
        shortGptUI.queue().launch(server_port=31415, height=1000, allowed_paths=["public/","videos/","fonts/"], share=self.colab, server_name="0.0.0.0")



if __name__ == "__main__":
    app = ShortGptUI()
    app.launch()


import signal

def signal_handler(sig, frame):
    print("Closing Gradio server...")
    import gradio as gr
    gr.close_all()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
