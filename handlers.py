import logging
import os
import tempfile
import requests
from telegram import Update, InputFile
from config import DEFAULT_CHANNEL, TARGET_CHANNEL
import sys
from PIL import Image

logger = logging.getLogger(__name__)

def send_post(context, content: dict):
    """
    Send a post to the target channel or chat.
    
    Args:
        context: The context from the scheduler
        content: Dict containing 'image_url', 'caption', and 'source'
    """
    import logging
    logger = logging.getLogger('handlers')
    try:
        # Use TARGET_CHANNEL from config as channel username (falls back to DEFAULT_CHANNEL if not set)
        channel = TARGET_CHANNEL
        if not channel:
            logger.error("No channel username provided for posting! Set TARGET_CHANNEL in environment variables.")
            return
            
        # Make sure the channel name starts with @ if it doesn't already
        if not channel.startswith('@'):
            channel = '@' + channel
            
        # Add hashtags and source attribution to the caption
        full_caption = f"{content['caption']}\n\n"
        
        if 'source' in content and content['source']:
            full_caption += f"Source: {content['source']}\n"
            
        full_caption += "#NakanoMiku #Miku #GotoubunNoHanayome #QuintessentialQuintuplets"
        
        # Get bot instance and send the photo
        bot = None
        if hasattr(context, 'bot'):
            bot = context.bot
            
        if not bot:
            logger.error("Could not get bot instance!")
            return
            
        try:
            # First download the image to a temporary file
            image_url = content['image_url']
            logger.info(f"Downloading image from: {image_url[:50]}...")
            
            # Create a temporary file
            temp_file = None
            try:
                # Download the image
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()  # Raise error for bad status codes
                
                # Get file extension from content type if possible
                content_type = response.headers.get('content-type', '')
                extension = '.jpg'  # Default extension
                if 'png' in content_type:
                    extension = '.png'
                elif 'gif' in content_type:
                    extension = '.gif'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    extension = '.jpg'
                
                # Create a temporary file with the appropriate extension
                fd, temp_file = tempfile.mkstemp(suffix=extension)
                os.close(fd)  # Close the file descriptor
                
                # Write the image data to the temporary file
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Image downloaded successfully to: {temp_file}")
                
                from PIL import Image
                
                # Check image dimensions and resize if needed
                try:
                    with Image.open(temp_file) as img:
                        width, height = img.size
                        logger.info(f"Image dimensions: {width}x{height}")
                        
                        # If image is very large or has unusual dimensions, resize it
                        if width > 5000 or height > 5000 or width < 10 or height < 10:
                            logger.info("Image has unusual dimensions, resizing...")
                            # Calculate new dimensions
                            max_size = 1280
                            if width > height:
                                new_width = min(width, max_size)
                                new_height = int(height * (new_width / width))
                            else:
                                new_height = min(height, max_size)
                                new_width = int(width * (new_height / height))
                            
                            # Resize image
                            img = img.resize((new_width, new_height), Image.LANCZOS)
                            img.save(temp_file)
                            logger.info(f"Image resized to {new_width}x{new_height}")
                except Exception as img_err:
                    logger.error(f"Error processing image: {img_err}")
                
                # Send the image from the temporary file
                try:
                    with open(temp_file, 'rb') as photo_file:
                        bot.send_photo(
                            chat_id=channel,
                            photo=InputFile(photo_file),
                            caption=full_caption
                        )
                    logger.info(f"Successfully posted content to {channel}")
                except Exception as send_err:
                    logger.error(f"Error sending from file: {send_err}")
                    # Fall back to direct URL
                    logger.info("Falling back to direct URL due to send error...")
                    bot.send_photo(
                        chat_id=channel,
                        photo=image_url,
                        caption=full_caption
                    )
                    logger.info("Posted using direct URL instead")
                
            except requests.exceptions.RequestException as req_err:
                logger.error(f"Error downloading image: {req_err}")
                # Fall back to direct URL if download fails
                logger.info("Falling back to direct URL...")
                bot.send_photo(
                    chat_id=channel,
                    photo=image_url,
                    caption=full_caption
                )
                logger.info(f"Successfully posted content using direct URL to {channel}")
                
            finally:
                # Clean up the temporary file
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        logger.debug(f"Temporary file {temp_file} removed")
                    except Exception as rm_err:
                        logger.warning(f"Failed to remove temporary file: {rm_err}")
                
        except Exception as e:
            if "Forbidden" in str(e) and "bot is not a member" in str(e):
                logger.error(f"Error: Bot doesn't have permission to post to {channel}. "
                            f"Make sure to add the bot as an administrator to this channel with 'Post Messages' permission.")
            else:
                logger.error(f"Error sending photo: {e}")
        
    except Exception as e:
        logger.error(f"Error sending post: {e}")
