import asyncio

from Automations.Background_listener import listen_forever
from Automations.Project_create import create_project
from Automations.Gpt_Code import generate_code
from Automations.Editor_writer import write_code_to_editor
from Automations.Gui_feedback import gui_confirm
from Automations.Error_handler import handle_error
from Automations.NLP_parser import extract_whatsapp_details

from Backend.voiceAuth import verify_voice
from Backend.core import call_main_executor


async def run_voice_automations_async():

    print("🎧 Voice automation started")

    loop = asyncio.get_running_loop()

    while True:

        # ⚠ run blocking microphone listener safely
        data = await asyncio.to_thread(next_command_safe)

        if not data:
            continue

        try:
            command = data.lower().strip()
            print("🗣️ Heard:", command)

            # 🔐 VOICE AUTH
            if not verify_voice():
                print("🚫 Unauthorized voice")
                continue

            print("✅ Voice verified")

            # --------------------------------------------------
            # SEND TO MAIN AI FIRST
            # --------------------------------------------------

            future = call_main_executor(command)

            if future:
                # give AI small time to react
                await asyncio.sleep(0.3)
                continue

            # --------------------------------------------------
            # FALLBACK AUTOMATION
            # --------------------------------------------------

            parsed = extract_whatsapp_details(command)

            if isinstance(parsed, tuple):
                action, name, message = parsed
                parsed = {
                    "action": action,
                    "name": name,
                    "message": message
                }

            action = parsed.get("action")

            if action == "create_project":
                create_project(parsed.get("project", "mywebsite"))
                gui_confirm("Project created")

            elif action == "write_code":
                code = generate_code(
                    parsed.get("prompt", "Create a full stack web app")
                )
                write_code_to_editor(code)
                gui_confirm("Code written")

        except Exception as e:
            handle_error(e)


# --------------------------------------------------
# SAFE GENERATOR WRAPPER
# --------------------------------------------------

_listener = listen_forever()


def next_command_safe():
    """
    Safely fetch next microphone command
    """
    try:
        data = next(_listener)
        return data[1] if isinstance(data, tuple) else data
    except StopIteration:
        return None
