import re

with open("c:\\pdf-chatbot\\app.py", "r", encoding="utf-8") as f:
    content = f.read()

old_code = """
                            final_img_url = None
                            for line in response.iter_lines():
                                if line:
                                    decoded_line = line.decode('utf-8')
                                    if decoded_line.startswith('data: '):
                                        data_str = decoded_line[6:]
                                        try:
                                            data = json.loads(data_str)
                                            if data.get('status') == 'processing':
                                                status_text.info(f"Progress: {data.get('message', 'Generating...')}")
                                            elif data.get('status') == 'complete':
                                                final_img_url = data.get('imageUrl')
                                                break
                                            elif data.get('status') == 'error':
                                                status_text.error(f"Generation Error: {data.get('message')}")
                                                break
                                        except json.JSONDecodeError:
                                            pass
                                            
                            if final_img_url:
                                status_text.success("✨ Asset generated successfully!")
                                img_container.image(final_img_url, use_container_width=True)
                            else:
                                status_text.error("Failed to retrieve image URL from API.")
"""

new_code = """
                            final_img_url = None
                            api_error = None
                            for line in response.iter_lines():
                                if line:
                                    decoded_line = line.decode('utf-8')
                                    if decoded_line.startswith('data: '):
                                        data_str = decoded_line[6:]
                                        try:
                                            data = json.loads(data_str)
                                            if data.get('status') == 'processing':
                                                status_text.info(f"Progress: {data.get('message', 'Generating...')}")
                                            elif data.get('status') == 'complete':
                                                final_img_url = data.get('imageUrl')
                                                break
                                            elif data.get('status') == 'error':
                                                api_error = data.get('message', data.get('error', 'Unknown API Error'))
                                                break
                                        except json.JSONDecodeError:
                                            pass
                                            
                            if final_img_url:
                                status_text.success("✨ Asset generated successfully!")
                                img_container.image(final_img_url, use_container_width=True)
                            elif api_error:
                                status_text.error(f"API Error: {api_error}")
                            else:
                                status_text.error("Failed to retrieve image URL from API (No error provided).")
"""

content = content.replace(old_code.strip(), new_code.strip())

with open("c:\\pdf-chatbot\\app.py", "w", encoding="utf-8") as f:
    f.write(content)
