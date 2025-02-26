import os
import math
import base64
import subprocess

from PIL import Image
import PIL.Image
import nodriver as nd
from google import genai
import shutil


from pywebio import start_server, config
from pywebio.input import file_upload, actions 
from pywebio.output import put_text, put_success, scroll_to, use_scope, put_error, put_buttons,clear


# تحميل المتغيرات من ملف .env

#put_text("START")  # رسالة أولية في الواجهة

# إعداد متغيرات الكود الأصلي
COOKIES_FILE = '.session.dat'
TARGET_URL = 'https://submit.shutterstock.com/en/portfolio/not_submitted/photo'

# سنستخدم مجلد "images" لرفع الصور
IMAGES_FOLDER = 'images'


# دوال المساعدة (بنفس الكود الأصلي)
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        put_text(f"Error encoding image ❌: {e}")
        return None

def convert_to_jpg(input_path, output_path):
    with Image.open(input_path) as img:
        rgb_img = img.convert('RGB')
        rgb_img.save(output_path, 'JPEG')

def resize_image(input_path, output_path):
    img = Image.open(input_path)
    width, height = img.size
    current_pixels = width * height
    target_pixels = 4_100_000  # 4 ميجابكسل

    if current_pixels < target_pixels:
        scaling_factor = math.sqrt(target_pixels / current_pixels)
        new_width = int(round(width * scaling_factor))
        new_height = int(round(height * scaling_factor))
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(output_path)
        
        put_text("Size changed" )
    else:
        img.save(output_path)
        put_text("Size not changed")

def get_image_details(api_key, model, image_path):
    image = PIL.Image.open(image_path)
    response = api_key.models.generate_content(
        model=model,
        contents=[ image , """I need three elements for this image to sell on Shutterstock:

Description: I want a description of this image to sell it on Shutterstock, so that the description does not exceed 200 characters (almost 190 characters) and the description contains words that help spread the image. Remove quotes mark from the beginning and end of the description.
**DESCRIPTION**
[description here]

Keywords: Give me 30-45 (Less than 50) English keywords for this image to sell on Shutterstock. Preferably one-word keywords, separated by commas. Avoid spelling errors, repetition, and punctuation at the end, Write all words in small letters.
**KEYWORDS**
[keywords here]

Categories: 1-2 categories from this list (one per line):
Abstract, Animals/Wildlife, Arts, Backgrounds/Textures, Beauty/Fashion, 
Buildings/Landmarks, Business/Finance, Celebrities, Education, Food and drink, 
Healthcare/Medical, Holidays, Industrial, Interiors, Miscellaneous, Nature, 
Objects, Parks/Outdoor, People, Religion, Science, Signs/Symbols, 
Sports/Recreation, Technology, Transportation, Vintage.
**CATEGORIES**
[category1]
[category2 (optional)]"""])
    
    put_text("Generated details from genai:")
    put_text(response.text)
    
    sections = {
        'description': '',
        'keywords': '',
        'categories': []
    }
    current_section = None
    for line in response.text.split('\n'):
        line = line.strip()
        if line.startswith('**DESCRIPTION**'):
            current_section = 'description'
        elif line.startswith('**KEYWORDS**'):
            current_section = 'keywords'
        elif line.startswith('**CATEGORIES**'):
            current_section = 'categories'
        elif current_section:
            if current_section == 'description':
                sections['description'] += line + ' '
            elif current_section == 'keywords':
                sections['keywords'] += line
            elif current_section == 'categories' and line:
                sections['categories'].append(line.split('/')[0].strip())

    sections['description'] = sections['description'].strip()[:200]
    keywords = sections['keywords'].replace(';', ',')
    keywords_list = [k.strip().replace('_', ' ') for k in keywords.split(',') if k.strip()]
    seen = set()
    unique_keywords = []
    for kw in keywords_list:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    keywords = ', '.join(unique_keywords)

    valid_categories = {'Abstract', 'Animals/Wildlife', 'Arts', 'Backgrounds/Textures',
                       'Beauty/Fashion', 'Buildings/Landmarks', 'Business/Finance',
                       'Celebrities', 'Education', 'Food and drink', 'Healthcare/Medical',
                       'Holidays', 'Industrial', 'Interiors', 'Miscellaneous', 'Nature',
                       'Objects', 'Parks/Outdoor', 'People', 'Religion', 'Science',
                       'Signs/Symbols', 'Sports/Recreation', 'Technology', 'Transportation', 'Vintage'}

    categories = []
    for cat in sections['categories']:
        if cat in valid_categories:
            categories.append(cat)
        else:
            for valid_cat in valid_categories:
                if cat.lower() in valid_cat.lower():
                    categories.append(valid_cat)
                    break
    categories = list(dict.fromkeys(categories[:2]))
    return sections['description'], keywords, categories

def modify_metadata(image_path, description, keywords):
    try:
        cmd = [
            "exiftool",
            "-overwrite_original",
            f"-XMP:Description={description.strip()}"
        ]
        for keyword in keywords.split(','):
            cmd.append(f"-XMP:Subject={keyword.strip()}")
        cmd.append(image_path)
        subprocess.run(
            cmd, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        put_text("Metadata updated ✅")
        return True
    except subprocess.CalledProcessError as e:
        put_text(f"Metadata Error: {e.stderr.decode()}")
        return False
    except Exception as e:
        put_text(f"Metadata Error: {str(e)}")
        return False

async def load_cookies_and_navigate(browser):
    def search_dat():
    # إرجاع أول ملف .dat في الدليل
      dat_files = [f for f in os.listdir() if f.endswith('.dat') and os.path.isfile(f)]
      return dat_files[0] if dat_files else put_error("error in cookie")
    try:
         dat_file = search_dat()
        
         await browser.cookies.load(dat_file)
         page = await browser.get(TARGET_URL)
         return page
        
        
    except Exception as e:
        put_error(f"Cookies error ❌: {e}")
        return None



async def upload_images(browser, page, api_key, model):
    try:
        await page.set_window_size(width=700, height=1000)
        images_path = os.path.abspath(IMAGES_FOLDER)
        image_files = [os.path.join(images_path, f) for f in os.listdir(images_path)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

        if not image_files:
            put_text("No images in the folder 📁")
            await page.sleep(5)
            return False

        for image_path in image_files:
            # تحويل الصورة إلى jpg إذا كانت png أو webp
            if image_path.lower().endswith(('.png', '.webp')):
                jpg_path = image_path.rsplit('.', 1)[0] + '.jpg'
                convert_to_jpg(image_path, jpg_path)
                os.remove(image_path)
                image_path = jpg_path

            # تغيير الحجم للصورة لتصبح حوالي 4 ميجابكسل
            resized_path = image_path.rsplit('.', 1)[0] + '_resized.jpg'
            resize_image(image_path, resized_path)
            os.remove(image_path)
            image_path = resized_path

            image_name = os.path.basename(image_path)
            try:
                put_text("Getting image details...")
                description, keywords, categories = get_image_details(api_key, model, image_path)
                modify_metadata(image_path=image_path, description=description, keywords=keywords)
            except Exception as e:
                put_text(f"Error getting image details ❌: {e}")
                description, keywords, categories = "", "", []
            
            # قم بتغيير اسم الصورة الى اسم التصنيفات التي ولدها الذكاء الاصطناعي
            if categories:
    
               new_image_name = ", ".join(category.replace("/", "-") for category in categories) + ".jpg"
    
               new_image_path = os.path.join(os.path.dirname(image_path), new_image_name)
               os.rename(image_path, new_image_path)
    
               put_text(f"Image renamed to: {new_image_name}")
               image_path = new_image_path
               image_name = new_image_name
               
            try:
                rejectcooki = await page.find("Reject All", timeout=0.01)
                await rejectcooki.click()
            except Exception:
                pass

            upload_button = await page.wait_for('[data-testid="desktop-upload-button"]', timeout=20)
            await upload_button.click()

            file_input = await page.wait_for('input[type="file"]', timeout=6)
            await file_input.send_file(image_path)
            put_text("Image uploaded ✅")

            try:
                xdownload = await page.select('[data-testid="snackbar-close-icon"]', timeout=4)
                await xdownload.mouse_click()
            except Exception:
                pass

            image_element = await page.wait_for(f'img[data-testid^="card-media-{image_name}"]', timeout=15)
            await image_element.click()
            try:
                xdownload = await page.select('[data-testid="snackbar-close-icon"]', timeout=4)
                await xdownload.mouse_click()
            except Exception:
                pass

            put_text("Image selected ✅")
            await page.sleep(1)

            try:
                # Category 1
                if categories and categories[0]:
                    put_text(f"Category 1: {categories[0]}")
                    category1_selector = await page.select('#mui-component-select-category1', timeout=5)
                    categorie_view = await page.select('[name="imageType"]')
                    await categorie_view.scroll_into_view()
                    await page.sleep(1.2)
                    await category1_selector.mouse_click()
                    category1_option = await page.wait_for(f'[data-testid="{categories[0]}"]', timeout=5)
                    if category1_option:
                        await category1_option.scroll_into_view()
                        await category1_option.click()
                        put_text("Category 1 selected ✅")
                    else:
                        put_text(f"Category option {categories[0]} not found ❌")
                        await page.save_screenshot()
                # Category 2
                if len(categories) > 1 and categories[1].strip():
                    category2_text = categories[1].strip()
                    if category2_text:
                        put_text(f"Category 2: {category2_text}")
                        category2_selector = await page.select('#mui-component-select-category2', timeout=5)
                        await categorie_view.scroll_into_view()
                        await page.sleep(1.4)
                        await category2_selector.mouse_click()
                        category2_option = await page.wait_for(f'[data-testid="{category2_text}"]', timeout=5)
                        if category2_option:
                            await category2_option.scroll_into_view()
                            await category2_option.click()
                            put_text("Category 2 selected ✅")
                        else:
                            put_text(f"Category option {category2_text} not found ❌")
                            await page.save_screenshot()
                else:
                    put_text("Category 2 is None ✅")
            except Exception as e:
                put_text(f"Error selecting categories ❌: {e}")
                await page.save_screenshot()

            try:
                submit_button = await page.select('[data-testid="edit-dialog-submit-button"]', timeout=5)
                await page.sleep(1)
                await submit_button.click()
                put_text("Image submitting...")
                submit = await page.find("1 asset has been submitted successfully.", best_match=True, timeout=8)
                if submit:
                    put_success("Image submitted 💀")
                else:
                    Invalid = await page.find("Invalid keywords removed", best_match=True, timeout=5)
                    if Invalid:
                        await submit_button.click()
                        put_text("Image submitting 2...")
                        submit = await page.find("1 asset has been submitted successfully.", best_match=True, timeout=8)
                        if submit:
                         put_success("Image submitted 💀")
                    else:
                     await page.save_screenshot()
                     save = await page.select('[data-testid="edit-dialog-save-button"]', timeout=5)
                     await save.click()
                     put_text("Saving...")
                     saving = await page.find("Your edit has been updated successfully.", best_match=True, timeout=7)
                     if saving:
                         put_success("Image saved ✔")
                     else:
                        put_error("Error in save ❌")
                        await page.save_screenshot()
            except Exception:
                put_text("Submission step encountered an error ❌")
            
            os.remove(image_path)
            
            # تأكيد تمرير كل خطوة على الواجهة
            scroll_to('bottom')
        return True

    except Exception as e:
        put_text(f"Error in uploading images ❌: {e}")
        await page.save_screenshot()
        return False
   



   



@config(theme="dark")
def web_main():
    def move_file(source_directory, filename):
       source_path = os.path.join(source_directory, filename)
       if os.path.isfile(source_path):
           shutil.move(source_path, os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
           upload_image()
        
       else:
           put_error(f'File {filename} not found.')

    def reload():
        put_buttons([
                {"label": "📂 رفع ملف session.dat", "value": "session"},
                {"label": "🖼️ رفع صور جديدة", "value": "images"}
            ], onclick=[lambda: upload_session(), lambda: upload_image()])

    def yazan(): 
       upload_image()
    def Ahmed():
       with use_scope('ahmed', clear=True):
       
          buttons = [
    {'label': 'A1', 'value': 'A1', 'color': 'secondary'},
    {'label': 'A2', 'value': 'A2', 'color': 'secondary'},
    {'label': 'A3', 'value': 'A3', 'color': 'secondary'}
    
]
          put_buttons(buttons, onclick=[lambda: move_file('/workspaces/codespaces-flask/seasions ', 'a1.dat'), lambda: move_file('/workspaces/codespaces-flask/seasions ', 'a2.dat'), lambda: move_file('/workspaces/codespaces-flask/seasions ', 'a3.dat')])
          

       


    def zaid():

       upload_image()



    def Moh():

    

       upload_image()

        
    def upload_session():

        
        """دالة لرفع ملف session.dat"""
        with use_scope('upload', clear=True):
           
           

           buttons = [
    {'label': 'Yazan', 'value': 'yazan', 'color': 'light'},
    {'label': 'Zaid', 'value': 'zaid', 'color': 'success'},
    {'label': 'Ahmed', 'value': 'ahmed', 'color': 'secondary'},
    {'label': 'Moh', 'value': 'moh', 'color': 'info'}
]
           put_buttons(buttons, onclick=[lambda: yazan(), lambda: zaid(), lambda: Ahmed(), lambda: Moh()])
           
            

            # زر للانتقال إلى رفع الصور
           

    def upload_image():
        
        clear('upload')
        with use_scope('images', clear=True):
            image_files = file_upload(
                "📂 اختر الصور",
                accept="image/*", 
                multiple=True, 
                required=True,
            )

            # تنظيف مجلد الصور قبل رفع الجديدة
            os.makedirs(IMAGES_FOLDER, exist_ok=True)
            for f in os.listdir(IMAGES_FOLDER):
                os.remove(os.path.join(IMAGES_FOLDER, f))
            
            for img in image_files:
                img_path = os.path.join(IMAGES_FOLDER, img['filename'])
                with open(img_path, 'wb') as f:
                    f.write(img['content'])
            
            put_text(f"✅ تم تحميل {len(image_files)} صور")

            # انتظار المستخدم للبدء في العملية
            actions("اضغط على الزر ", buttons=[{"label": "Start", "value": "start"}] )

            # بدء العملية الأساسية
            nd.loop().run_until_complete(process_all_images(api="AIzaSyCyDf4n9lbP22_ipDr1rudmHb7ejZuBlJY"))
            reload()
            

            # إضافة زرين للرجوع إلى رفع session.dat أو الصور
            

    # عرض قائمة رفع ملف session.dat في البداية
    upload_session()

async def process_all_images(api):
    
    # بدء المتصفح باستخدام nodriver
    browser = await nd.start(
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--headless=new",
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "--disable-infobars",
            "--disable-extensions",
        ]
    )
    try:
        page = await load_cookies_and_navigate(browser)
        if page:
            api_key = genai.Client(api_key=api)
            model = "gemini-2.0-pro-exp-02-05"   # gemini-2.0-pro-exp-02-05       gemini-2.0-flash
            while True:
                upload_success = await upload_images(browser, page, api_key, model)
                if not upload_success:
                    put_text("aaaaaaaaaaaaaaa")
                    break
                images_path = os.path.abspath(IMAGES_FOLDER)
                image_files = [f for f in os.listdir(images_path)
                               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if not image_files:
                    browser.stop()
                    os.makedirs("/workspaces/codespaces-flask/seasions ", exist_ok=True)
                    [shutil.move(f, "/workspaces/codespaces-flask/seasions ") for f in os.listdir() if f.endswith(".dat")]
                    break
            
    except Exception as e:
        put_error(f"Main error ❌: {e}")




if __name__ == '__main__':
    start_server(web_main, port=8080, debug=True)
    
    
