import os
import pkgutil
import random
import re
import subprocess
import time

from unbiased.unbiasedObjects import *

from PIL import Image


#take in a url and delimiters, return twitter card
def buildArticle(url, sourceName, scratchDir, encoding=None):#, titleDelStart, titleDelEnd, imgDelStart, imgDelEnd):

    debugging=False
    if debugging:
        print(sourceName)
        print(url)
        print()

    temp_article = os.path.join(scratchDir, 'temp_article.html')

    #download url
    #os.system('wget -q -O scratch/temp_article.html --no-check-certificate '+url)
    subprocess.check_call(['wget', '-q', '-O', temp_article, '--no-check-certificate', url])

    #read the file in
    f=open(temp_article, 'r', encoding="utf8")
    content=f.read()
    f.close()

    try:
        if sourceName=='The Guardian':
            #The Guardian puts an identifying banner on their og:images
            #grab the main image from the page instead

            #scenario 1: regular image
            if '<img class="maxed' in content:
                img=content.split('<img class="maxed', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            #scenario 2: video in image spot
            elif '<meta itemprop="image"' in content:
                img=content.split('<meta itemprop="image"', 1)[1]
                img=img.split('content="', 1)[1].split('"')[0]
            #scenario 3: photo essays
            elif '<img class="immersive-main-media__media"' in content:
                img=content.split('<img class="immersive-main-media__media"', 1)[1]
                img=img.split('src="', 1)[1].split('"')[0]
            
        else:
            if 'og:image' in content:
                img=content.split('og:image" content=')[1][1:].split('>')[0]
            elif sourceName=='ABC News':
                img='https://c1.staticflickr.com/7/6042/6276688407_12900948a2_b.jpgX'
            if img[-1]=='/':
                #because the quote separator could be ' or ", 
                #trim to just before it then lop it off
                img=img[:-1].strip()
            img=img[:-1]

        if debugging:
            print(img)

        title=content.split('og:title" content=')[1][1:].split('>')[0]
        if title[-1]=='/':
            title=title[:-1].strip()
        title=title[:-1]

        if debugging:
            print(title)


        author=''
        if sourceName=='The Blaze':
            if 'class="article-author">' in content:
                author=content.split('class="article-author">')[1].split('<')[0]
            elif 'class="article-author" href="' in content:
                author=content.split('class="article-author" href="')[1]
                author=author.split('>')[1].split('<')[0].strip()
        else:
            authorTags=['article:author', 'dc.creator', 'property="author']
            for tag in authorTags:
                if tag in content:
                    author=content.split(tag+'" content=')[1][1:].split('>')[0]
                    author=author[:-1]
                    #trim an extra quotation mark for The Hill
                    if sourceName=='The Hill':
                        author=author.split('"', 1)[0]
                    break

        if debugging:
            print(author)


        if 'og:description' in content:
            description=content.split('og:description" content=')[1][1:].split('>')[0]
            if description[-1]=='/':
                description=description[:-1].strip()
            description=description[:-1]
        else:
            if sourceName=='The Hill':
                description=content.split('div class="field-items"')[-1]
                description=re.sub('<[^<]+?>', '', description)
                description=description[1:200]
            else:
                print("SHOULDN'T GET HERE")

        #strip out self-references
        description=description.replace(sourceName+"'s", '***')
        description=description.replace(sourceName+"'", '***')
        description=description.replace(sourceName, '***')

        if debugging:
            print(description)


        a=Article(title, url, img, description, sourceName, author)
        return a

    except Exception:
        print('^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('\tARTICLE PARSING ERROR')
        print('SOURCE: '+sourceName)
        print('URL: \t'+url)
        print('^^^^^^^^^^^^^^^^^^^^^^^^^ \n\n')
        return None


def buildOutput(newsSourceArr, webroot):
    #read in the template html file
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('unbiased', 'html_template'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('unbiased.jinja.html')

    #set the random order for sources
    h1RandomSources=[]
    while len(h1RandomSources)<4:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        if len(newsSourceArr[x].h1Arr)>0:
            if x not in h1RandomSources:
                h1RandomSources.append(x)
        else:
            print('\n\n@@@@\nNo H1 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')

    #For h2s and h3s, select N random sources (can repeat), then
    #a non-repetitive random article from within
    h2RandomPairs=[]
    while len(h2RandomPairs) < 6:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        if len(newsSourceArr[x].h2Arr) > 0:
            y=random.sample(range(len(newsSourceArr[x].h2Arr)), 1)[0]
            pair=[x,y]
            if not pair in h2RandomPairs:
                h2RandomPairs.append(pair)
        else:
            print('\n\n@@@@\nNo H2 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')

    h3RandomPairs=[]
    while len(h3RandomPairs) < 12:
        x=random.sample(range(len(newsSourceArr)), 1)[0]
        print(newsSourceArr[x].name)
        if len(newsSourceArr[x].h3Arr) > 0:
            y=random.sample(range(len(newsSourceArr[x].h3Arr)), 1)[0]
            pair=[x,y]
            if not pair in h3RandomPairs:
                h3RandomPairs.append(pair)
        else:
            print('\n\n@@@@\nNo H3 stories in '+newsSourceArr[x].name+'\n@@@@\n\n')

    # collect articles for each section
    image_index = 0

    top_stories = []
    for i in range(len(h1RandomSources)):
        source=newsSourceArr[h1RandomSources[i]]
        randomArticle=random.sample(range(len(source.h1Arr)), 1)[0]
        article=source.h1Arr[randomArticle]
        img_name = pullImage(article.img, image_index, webroot, 350, 200)
        image_index += 1
        article.img = img_name
        top_stories.append(article)

    middle_stories = []
    for i in range(len(h2RandomPairs)):
        pair=h2RandomPairs[i]
        article=newsSourceArr[pair[0]].h2Arr[pair[1]]
        img_name = pullImage(article.img, image_index, webroot, 150, 100)
        image_index += 1
        article.img = img_name
        middle_stories.append(article)

    bottom_stories = []
    for i in range(len(h3RandomPairs)):
        pair=h3RandomPairs[i]
        article=newsSourceArr[pair[0]].h3Arr[pair[1]]
        bottom_stories.append(article)

    sourcesStr=''
    for i in range(len(newsSourceArr)-1):
        sourcesStr+=newsSourceArr[i].name+', '
    sourcesStr+=newsSourceArr[-1].name
    print('Successfully parsed: '+sourcesStr)

    timestamp=time.strftime("%a, %b %-d, %-I:%M%P %Z", time.localtime())

    html = template.render(
        timestamp = timestamp,
        top_stories = top_stories,
        middle_stories = middle_stories,
        bottom_stories = bottom_stories,
        sources = sourcesStr,
    )


    #return updated text
    return html

def printOutputHTML(outputHTML, outDir):
    timestamp=time.strftime("%a, %b %-d, %-I:%M%P %Z", time.localtime())
    outputHTML=outputHTML.replace('xxTimexx', timestamp)

    with open(os.path.join(outDir, 'index.html'), 'w') as fp:
        fp.write(outputHTML)

    # copy over the template css file
    css = pkgutil.get_data('unbiased', 'html_template/unbiased.css')
    css = css.decode('utf8')
    with open(os.path.join(outDir, 'unbiased.css'), 'w') as fp:
        fp.write(css)

def buildNewsSourceArr(sourceList, scratchDir):

    #build the data structure
    i=0
    listLen=len(sourceList)
    while i < listLen:
        source=sourceList[i]

        if type(source) is NewsSource2:
            i+=1
            continue

        url=source.url

        temp_file = os.path.join(scratchDir, 'temp{}.html'.format(i))

        #download file
        #os.system('wget -q -O scratch/temp'+str(i)+'.html --no-check-certificate '+url)
        subprocess.check_call(['wget', '-q', '-O', temp_file, '--no-check-certificate', url])

        #read file
        f=open(temp_file, 'r', encoding="utf8")
        content=f.read()
        f.close()
        
        #delete file MAYBE DON'T DO THIS? CAUSES OS ERRORS
        #os.remove(temp_file)

        #add stories etc to the NewsSource object
        h1s, h2s, h3s=extractURLs(content, source)
        
        #build the Article objects and add to newsSource's appropriate list
        if h1s!=None and h2s!=None:
            for url in h1s:
                article=buildArticle(url, source.name, scratchDir)
                if article!=None: source.addArticle(article, 1) #sourceList[i].h1Arr.append(article)
            for url in h2s:
                article=buildArticle(url, source.name, scratchDir)
                if article!=None: sourceList[i].h2Arr.append(article)
            for url in h3s:
                article=buildArticle(url, source.name, scratchDir)
                if article!=None: sourceList[i].h3Arr.append(article)
            i+=1
        else:
            sourceList.remove(source)
            listLen-=1

            
    #return the original sourceList,
    #since everything should have been modified in place
    return sourceList        

def pullImage(url, index, webroot, width=350, height=200):
    extension = url.split('.')[-1].split('?')[0]
    img_name = 'img{}.{}'.format(index, extension)
    out_file = os.path.join(webroot, img_name)
    try:
        subprocess.check_call(['wget', '-q', '-O', out_file, '--no-check-certificate', url])
    except Exception:
        return ''
    img = Image.open(out_file)
    img.resize((width, height))
    jpg_name = 'img{}.jpg'.format(index)
    img.save(os.path.join(webroot, jpg_name), 'JPEG')
    return jpg_name
