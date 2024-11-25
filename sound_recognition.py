import speech_recognition as sr
import google.generativeai as genai #改openai
import configparser
import re
import json

# 創建 ConfigParser 對象(api key會放在config裡避免直接取用，這個部分你們可能要改成openai)
config = configparser.ConfigParser()
config.read('config.ini')
GOOGLE_API_KEY = config['API']['api_key']
genai.configure(api_key=GOOGLE_API_KEY)

# 把LLM產稱的內容格式化後產生json檔到指定路徑
def extract_and_dump_json(sample_text, output_file_path):
    pattern = r"```json(.*?)```"
    json_part = re.search(pattern, sample_text, re.DOTALL)
    
    # Extracted JSON text
    extracted_json = json_part.group(1).strip() if json_part else None
    
    if extracted_json:
        parsed_json = json.loads(extracted_json)
        
        # Dump the parsed JSON to a file
        with open(output_file_path, 'w') as json_file:
            json.dump(parsed_json, json_file, indent=4)
        
        return output_file_path
    else:
        return None
# 呼叫LLM 產生內容
def generate_json(instruction):
    model = genai.GenerativeModel('gemini-1.5-flash') #要改成openai
    
    # Prepare the prompt(改這個部分可以產生你們想要的json檔)
    prompt = f"""instruction : {instruction}

    Please understand the equipment and the order in this instruction, and convert them into the following JSON schema:

    [
        {{
            "equipment": "<description of equipment>",
            "order": "<step-by-step order>"
        }}
    ]

    Please return this in valid JSON format.
    """
    
    print(prompt)  # For debugging purposes
    
    # Generate response from the model
    response = model.generate_content(prompt).text
    return response


# 創建一個Recognizer對象
recognizer = sr.Recognizer()

# 使用麥克風作為輸入源
with sr.Microphone() as source:
    print("請說話...")
    # 讓系統調整噪音
    recognizer.adjust_for_ambient_noise(source)
    # 獲取音頻數據
    audio_data = recognizer.listen(source)
    try:
        # 將音頻轉換成文字
        text = recognizer.recognize_google(audio_data, language="zh-TW")
        print("你說了: " + text)
        response = generate_json(text)
        print(response)
        path = "output.json"
        extract_and_dump_json(response,path)
    except sr.UnknownValueError:
        print(audio_data)
        print("無法識別語音")
    except sr.RequestError as e:
        print("請求失敗; {0}".format(e))
