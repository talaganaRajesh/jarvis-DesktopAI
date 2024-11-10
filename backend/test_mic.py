import speech_recognition as sr
import time

def test_microphone():
    # Create a recognizer instance
    r = sr.Recognizer()
    
    # List all available microphones
    print("Available Microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone [{index}]: {name}")
    
    try:
        # Use the default microphone
        with sr.Microphone() as source:
            print("\nAdjusting for ambient noise... Please wait...")
            r.adjust_for_ambient_noise(source, duration=2)
            print("\n🎤 Microphone is ready!")
            print("Please speak something...")
            
            while True:
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                    print("\nRecognizing...")
                    
                    try:
                        text = r.recognize_google(audio)
                        print(f"You said: {text}")
                    except sr.UnknownValueError:
                        print("Sorry, I couldn't understand that.")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        
                except sr.WaitTimeoutError:
                    print("No speech detected. Please try again...")
                    
                print("\nListening again...")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure your microphone is connected and working")
        print("2. Check if your microphone is set as the default recording device")
        print("3. Check if you have given microphone permissions to Python")
        print("4. Try running the script with administrator privileges")

if __name__ == "__main__":
    print("Starting voice recognition test...")
    test_microphone()