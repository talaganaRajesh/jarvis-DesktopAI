from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import logging
from utils.voice_handler import VoiceHandler
from utils.visual_handler import VisualHandler
from utils.system_commands import SystemCommands
import speech_recognition as sr

# Ensure the SpeechRecognition library is installed
# Run: pip install SpeechRecognition

# Ensure Flask and Flask-CORS libraries are installed
# Run: pip install Flask Flask-Cors

app = Flask(__name__)
# Enable CORS for all domains
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class DesktopAutomationController:
    def __init__(self):
        self.voice_enabled = False
        self.visual_enabled = False
        self.voice_handler = VoiceHandler()
        self.visual_handler = VisualHandler()
        self.system_commands = SystemCommands()
        
        self.voice_thread = None
        self.visual_thread = None
        self.command_history = []
        self.max_history = 100  # Maximum number of commands to keep in history

    def add_to_history(self, command_type, command, status):
        """Add command to history with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.command_history.append({
            "timestamp": timestamp,
            "type": command_type,
            "command": command,
            "status": status
        })
        
        # Keep only the last max_history commands
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

    def voice_recognition_loop(self):
        """Main loop for voice recognition"""
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            self.voice_handler.adjust_for_ambient_noise(source)
            logger.info("Voice recognition started")
            
            while self.voice_enabled:
                try:
                    command = self.voice_handler.listen_for_command(source)
                    if command:
                        logger.info(f"Voice command detected: {command}")
                        if self.system_commands.execute_command(command):
                            self.add_to_history("voice", command, "success")
                        else:
                            self.add_to_history("voice", command, "unknown command")
                except Exception as e:
                    logger.error(f"Error in voice recognition: {str(e)}")
                    self.add_to_history("voice", "error", str(e))

    def visual_recognition_loop(self):
        """Main loop for visual recognition"""
        logger.info("Visual recognition started")
        while self.visual_enabled:
            try:
                frame = self.visual_handler.capture_screen()
                if self.visual_handler.detect_gestures(frame):
                    logger.info("Gesture detected")
                    self.add_to_history("visual", "gesture", "detected")
                time.sleep(0.1)  # Prevent high CPU usage
            except Exception as e:
                logger.error(f"Error in visual recognition: {str(e)}")
                self.add_to_history("visual", "error", str(e))

    def start_voice_recognition(self):
        """Start voice recognition in a separate thread"""
        if not self.voice_enabled:
            self.voice_enabled = True
            self.voice_thread = threading.Thread(target=self.voice_recognition_loop)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            return True
        return False

    def stop_voice_recognition(self):
        """Stop voice recognition"""
        if self.voice_enabled:
            self.voice_enabled = False
            if self.voice_thread:
                self.voice_thread.join(timeout=1)
            return True
        return False

    def start_visual_recognition(self):
        """Start visual recognition in a separate thread"""
        if not self.visual_enabled:
            self.visual_enabled = True
            self.visual_thread = threading.Thread(target=self.visual_recognition_loop)
            self.visual_thread.daemon = True
            self.visual_thread.start()
            return True
        return False

    def stop_visual_recognition(self):
        """Stop visual recognition"""
        if self.visual_enabled:
            self.visual_enabled = False
            if self.visual_thread:
                self.visual_thread.join(timeout=1)
            return True
        return False

# Create controller instance
controller = DesktopAutomationController()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check if the server is running"""
    return jsonify({
        "status": "healthy",
        "voice_enabled": controller.voice_enabled,
        "visual_enabled": controller.visual_enabled
    })

@app.route('/toggle-voice', methods=['POST'])
def toggle_voice():
    """Toggle voice recognition on/off"""
    try:
        data = request.json
        enable = data.get('enabled', False)
        
        if enable:
            success = controller.start_voice_recognition()
        else:
            success = controller.stop_voice_recognition()
            
        return jsonify({
            "status": "success" if success else "no change",
            "voice_enabled": controller.voice_enabled
        })
    except Exception as e:
        logger.error(f"Error toggling voice recognition: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/toggle-visual', methods=['POST'])
def toggle_visual():
    """Toggle visual recognition on/off"""
    try:
        data = request.json
        enable = data.get('enabled', False)
        
        if enable:
            success = controller.start_visual_recognition()
        else:
            success = controller.stop_visual_recognition()
            
        return jsonify({
            "status": "success" if success else "no change",
            "visual_enabled": controller.visual_enabled
        })
    except Exception as e:
        logger.error(f"Error toggling visual recognition: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/command-history', methods=['GET'])
def get_command_history():
    """Get the command execution history"""
    limit = request.args.get('limit', default=50, type=int)
    return jsonify({
        "status": "success",
        "history": controller.command_history[-limit:]
    })

@app.route('/execute-command', methods=['POST'])
def execute_command():
    """Manually execute a command"""
    try:
        data = request.json
        command = data.get('command', '').lower()
        
        if controller.system_commands.execute_command(command):
            controller.add_to_history("manual", command, "success")
            return jsonify({
                "status": "success",
                "message": f"Command '{command}' executed successfully"
            })
        else:
            controller.add_to_history("manual", command, "unknown command")
            return jsonify({
                "status": "error",
                "message": f"Unknown command: {command}"
            }), 400
            
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/available-commands', methods=['GET'])
def get_available_commands():
    """Get list of available commands"""
    return jsonify({
        "status": "success",
        "commands": list(controller.system_commands.commands.keys())
    })

if __name__ == '__main__':
    # Add any startup initialization here
    logger.info("Starting Desktop Automation Server...")
    app.run(host='localhost', port=5000, debug=True)