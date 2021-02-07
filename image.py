def load_image(self, response):
    # кидаем в функцию http-строку и преобразуем ее в файл .png
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    # меняем размер до нужного нам 600х600
    map_file = map_file.resize((600, 600))
    # переделываем файл в тип pixmap и возвращаем его
    return QPixmap(self.map_file)
