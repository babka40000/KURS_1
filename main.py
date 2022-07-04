from pprint import pprint
from social_net import YaUploader, VkWorker

if __name__ == '__main__':
    id_vk = input('Введите ID или screen name пользователя вконтакте: ')
    quantity_foto = int(input('Введите количество загружаемых фото: '))

    ya_disk = YaUploader('setting.ini')
    ya_disk.create_catalog(str(id_vk))

    vk = VkWorker(id_vk, 'setting.ini', quantity_foto)
    vk_foto_list = vk.get_sort_foto_list()

    ya_disk.save_json_file('result.txt', ya_disk.upload_foto_list_from_vk(vk_foto_list, str(id_vk)))
