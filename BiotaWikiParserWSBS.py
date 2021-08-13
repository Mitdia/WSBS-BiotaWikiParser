import bs4
import requests


def check_link(link):
    if len(link.split(":")) > 2 or len(link.split("#")) > 1:
        return False
    elif "jpg" in link.split("."):
        return False
    return True


def get_all_links(link):
    links = []
    response = requests.get(link)
    if response is not None:
        html = bs4.BeautifulSoup(response.text, 'html.parser')
    for link in html.find_all("a"):
        link = link.attrs.get("href")
        if link == "" or link is None:
            continue
        link_parsed = link.split("/")
        if len(link_parsed) < 3:
            continue
        if link_parsed[1] == "wiki" and link_parsed[2] == "index.php":
            links.append(link)
    return links


def get_all_sublinks(link, links=[], used=[]):
    if links == []:
        file = open("links.txt", "r")
        links = file.read().split("\n")
        file.close()
    else:
        if link not in links:
            links.append(link)
    if link not in used and check_link(link):
        used.append(link)
        for new_link in get_all_links(link):
            new_link = "http://biota.wsbs-msu.ru" + new_link
            get_all_sublinks(new_link, links, used)
    return links


def save_all_links():
    links = get_all_sublinks("http://biota.wsbs-msu.ru/wiki/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0")
    fout = open("links.txt", "w")
    print(*links, sep="\n", file=fout)
    fout.close()


def get_bad_words():
    bad_file = open("bad_words.txt", "r",  encoding='utf-8')
    bad_words = bad_file.read().split("\n")
    for word in bad_words:
        if word == "":
            bad_words.remove(word)
    bad_file.close()
    return bad_words


def check_li_tag(text, database):
    parsed_text = text.split(" ")
    bad_words = get_bad_words()
    for word in bad_words:
        if word in parsed_text:
            return False
    if text == "":
        return False
    if text in database:
        return False
    if parsed_text[0] in ["var.", "f.", "F.", "Var.", "v."]:
        return False
    return True


def get_all_li_tags(link):
    result = []
    response = requests.get(link)
    if response is not None:
        html = bs4.BeautifulSoup(response.text, 'html.parser')
        for ul_tag in html.find_all("ul"):
            for li_tag in ul_tag.find_all("li"):
                if li_tag == "" or li_tag is None:
                    continue
                if not li_tag.has_attr("class") and not li_tag.has_attr("id"):
                    result.append(li_tag)
    return result


def format_text(text):
    text = text.replace("—", "-")
    text = text.replace("–", "-")
    text = text.replace("-", "~")
    text = "~".join([i.strip(" ") for i in text.split("~")])
    return text


def parseHTML(link, database=[]):
    fout = open("output.csv", "a", encoding='utf-8')
    print(link)
    response = requests.get(link)
    if response is not None:
        html = bs4.BeautifulSoup(response.text, 'html.parser')
        for ul_tag in html.find_all("ul"):
            for li_tag in ul_tag.find_all("li"):
                if li_tag == "" or li_tag is None:
                    continue
                if not li_tag.has_attr("class") and not li_tag.has_attr("id"):
                    sub_li_tags = li_tag.find_all("li")
                    if len(sub_li_tags) != 0:
                        text_start = li_tag.find(text=True, recursive=False).replace("\n", " ").strip(" ")
                        for sub_tag in sub_li_tags:
                            text_end = sub_tag.get_text().replace("\n", " ").strip(" ")
                            #print(text_end)
                            if check_li_tag(text_end, database):
                                #print(text_end)
                                database.append(text_end)
                            text = text_start + text_end
                            #print(text)
                            if check_li_tag(text, database):
                                print(format_text(text), link, file=fout, sep="~")
                                database.append(text)
                    else:
                        text = li_tag.get_text().replace("\n", " ")
                        #print(text)
                        if check_li_tag(text, database):
                                database.append(text)
                                print(format_text(text), link, file=fout, sep="~")
    fout.close()
    return database


def parse_all_saved_links(database=[]):
    fin = open("links.txt", "r")
    links = fin.read().split("\n")
    for link in links:
        if link != "":
            database = parseHTML(link, database)
    fin.close()
    return database


if __name__ == "__main__":
    fin = open("database.txt", "r", encoding='utf-8')
    database = fin.read().split("\n")
    fin.close()
    #save_all_links()
    database = parse_all_saved_links(database)
    fout = open("database.txt", "w", encoding='utf-8')
    print(*database, sep="\n", file=fout)
    fout.close()
