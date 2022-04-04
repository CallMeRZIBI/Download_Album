import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from youtube_dl import YoutubeDL

def start_webdriver():
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(options=options)
    return driver


def get_band(driver):
    print("Enter band's name: ")
    band = input()
    url = 'https://en.wikipedia.org/wiki/' + band + '_discography'
    driver.get(url)
    actual_band = driver.find_element(by=By.TAG_NAME, value='h1')
    actual_band_text = actual_band.text
    index_of_removal = actual_band_text.index(' discography')
    actual_band_text = actual_band_text[:index_of_removal]
    return actual_band_text

#/html/body/div[3]/div[3]/div[5]/div[1]/table[2]/tbody
def detect_albums(driver):
    table = driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[3]/div[5]/div[1]/table[2]/tbody')
    listTex = table.find_elements(by=By.TAG_NAME, value='i')

    filteredListText = list(filter(lambda x : x.text != 'citation needed', listTex))
    return filteredListText

def get_album(albums_list):
    i = 0
    for album in albums_list:
        s = '(' + str(i) + ') ' + album.text
        print(s)
        i += 1

    print('Choose album by number: ')
    id = input()
    chosen_one = albums_list[int(id)]
    return chosen_one.text

def get_songs(driver, album, band):
    album = album.replace(' ', '_')
    band = band.replace(' ', '_')
    url = 'https://en.wikipedia.org/wiki/' + album + '_(' + band + '_album)'
    driver.get(url)
    try:
        not_found = driver.find_elements(by=By.TAG_NAME, value='b')
        for element in not_found:
            if element.text == 'Wikipedia does not have an article with this exact name.':
                url = 'https://en.wikipedia.org/wiki/' + album
                driver.get(url)
                break
    except NoSuchElementException:
        url = 'https://en.wikipedia.org/wiki/' + album
        driver.get(url)

    invalid_url = driver.find_element(by=By.XPATH, value='/html/body/div[3]/div[3]/div[5]/div[1]/p')
    # Checking if wikipedia didn't find any other articles named 10,000 days
    if "may refer to:" in invalid_url.text:
        finds_list = driver.find_elements(by=By.TAG_NAME, value='a')
        i = 0
        for find in finds_list:
            if band not in find.text:
                i += 1
            else:
                break
        finds_list[i].click()

    tracklists = driver.find_element(by=By.CLASS_NAME, value='tracklist')
    tracks = tracklists.find_elements(by=By.TAG_NAME, value='td')
    songs_list = []
    for track in tracks:
        if track.text.count('"') >= 2:
            s = track.text[track.text.index('"') + 1:track.text.find('"', track.text.find('"') + 1)]    # finding the first and second " to remove them
            songs_list.append(s)
    songs_list = list(dict.fromkeys(songs_list))

    return songs_list

def find_song_url(song, band, driver):
    youtube_url = 'https://www.youtube.com/results?search_query=' + band + '+' + song
    driver.get(youtube_url)
    try:
        driver.find_element(by=By.XPATH, value='//*[@id="content"]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a').click()
    finally:
        time.sleep(0.5)
        url_to_song = driver.find_elements(by=By.ID, value='video-title')
        try:
            try:
                return url_to_song[0].get_attribute('href')
            except:
                return url_to_song[1].get_attribute('href')
        except:
            print('Failed to download ' + song + ' by ' + band)

def download_song(url):
    audio_downloader = YoutubeDL({'format':'bestaudio'})
    print('Downloading: ' + url)
    try:
        audio_downloader.extract_info(url)
    except Exception as e:
        print(e)

def download_songs(songs, band, driver):
    for song in songs:
        song_url = find_song_url(song, band, driver)
        download_song(song_url)

# MAIN
driver = start_webdriver()
band = get_band(driver)
albums = detect_albums(driver)
album = get_album(albums)
songs = get_songs(driver, album, band)
download_songs(songs, band, driver)

driver.quit()
