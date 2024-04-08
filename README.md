# 🚀 The Future of Typing

## Final Project Intelligent Interactive Systems (Winter 2023/24 Semester)

Submitted by:
- Idan Horowitz
- Jacob Link

## 📝 Description
We believe there is a new typing method which will emerge in the near future, due to the augmented reality tech being introduced to the world 🌎 

When comming accross the Wall Street Journal's review of the Apple VisionPro,

They noted: "...one big problem." (see minute 1:49: https://youtu.be/8xI10SFgzQ8?si=WRSPMa4We3VgLh3Q&t=105) 

We decided to create a new concept keyborad for the AR world, solving this problem.

![system on wsj](images/vis_in_wsj_review.png)

## 📦 Files Uploaded 

`algorithms.py`: handles prompting and processing of responses.

`prompts.py`: final prompts used for Gemini.

`whisper_speech_to_text.py`: speech to text engine using Whisper.

**`typing_interface.py`: final streamlit app**

`environment.yml`: environment config file (see use in 'how to run' below).

### mouse control interface:
|file name|mouse movement|mouse left click|features
|--|--|--|--
|`mouse_control_app_option_1.py`|nose|thumb-index click|--
|`mouse_control_with_fist_stop_mouse.py`|nose|thumb-index click|with left hand: open palm to start, close fist to stop the mouse moving
|`mouse_control_with_index.py`|right hand tip of index finger|left hand thumb-index click|--

📁 **images**: images used throughout the ReadMe file

## 🏃 How To Run
Follow these steps to get the application running: 
1. Click: https://typing-future-iis.streamlit.app
2. Clone the GitHub repository to your desired location:
   ```
   git clone https://github.com/Jacob-Link/typing_future_iis_project.git
   ```
   Navigate to the git directory:
   ```
   cd typing_future_iis_project
   ```
3. Create conda environment:
   ```
   conda env create --file=environment.yml
   ```
4. Activate environment created:
   ```
   conda activate typing_future_env
   ```
5. Run the mouse control interface chosen:
   ```
   python mouse_control_with_fist_stop_mouse.py
   ```
   > 🔔 **Note**:
   > This might request the permission for terminal to access camera and mouse control. rerun 5 after granting permission.

6. To start controling the mouse with your nose - present the camera with your left hand "open-palm" gesture.
 
7. Navigate to the window with the streamlit app running (url in point 1) and start typing.
   
> 🔔 **Import Notes**:
> - If you are using the mouse control program - make sure you are connected to 1 display only!the app does not support multiple displays.
> 
> - You can assess the keyboard alone without the mouse control app, by exploring the url presented in (1)


### Keyborad Result
![result](images/keyboard_result.png)

## 📬 Contact

jacob.link@campus.technion.ac.il

idanhorowitz@campus.technion.ac.il

## 📃 License

Use wisely, might be addictive.
If you are from 🍎, and want to use this to upgrade typing in the Vision Pro, we're open to offers. 😉
----------

We hope you enjoyed the experience.
❤️ 
If you liked this, give us a ⭐.  
