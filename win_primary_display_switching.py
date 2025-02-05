import win32api
import win32con
import time

# Определяем константы (их нет в win32con)
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

def get_monitors():
    """ Получает список всех активных мониторов и определяет текущий основной """
    primary_display = None
    secondary_display = None
    device_index = 0
    monitors_info = []

    while True:
        try:
            device = win32api.EnumDisplayDevices(None, device_index)
            if device.StateFlags & DISPLAY_DEVICE_ACTIVE:
                print(f"🖥 Дисплей найден: {device.DeviceName} "
                      f"{'(Текущий главный)' if device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE else ''}")

                if device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE:
                    primary_display = device.DeviceName
                else:
                    secondary_display = device.DeviceName

                # Получаем информацию о разрешении и координатах
                devmode = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                monitors_info.append({
                    'device_name': device.DeviceName,
                    'x': devmode.Position_x,
                    'y': devmode.Position_y,
                    'width': devmode.PelsWidth,
                    'height': devmode.PelsHeight
                })
                
                # Выводим координаты каждого дисплея
                print(f"  📍 Положение {device.DeviceName}: ({devmode.Position_x},{devmode.Position_y})")

            device_index += 1
        except win32api.error:
            break  # Больше дисплеев нет

    return primary_display, secondary_display, monitors_info

def set_display_position(device_name, x, y):
    """ Устанавливает позицию монитора """
#    print(f"  🛠 Устанавливаем положение для {device_name} на ({x}, {y})")  # Новый вывод
    devmode = win32api.EnumDisplaySettings(device_name, win32con.ENUM_CURRENT_SETTINGS)
    devmode.Position_x = x
    devmode.Position_y = y
    result = win32api.ChangeDisplaySettingsEx(device_name, devmode)
    
    if result == win32con.DISP_CHANGE_SUCCESSFUL:
        print(f"  ✅ Позиция дисплея {device_name} изменена на ({x}, {y})")
    else:
        print(f"  ❌ Ошибка изменения позиции дисплея {device_name}: {result}")

def set_primary_monitor(device_name):
    print(f"  ⇔ Переключаем основной монитор на {device_name}...")
    """ Устанавливает указанный монитор как основной """
    devmode = win32api.EnumDisplaySettings(device_name, win32con.ENUM_CURRENT_SETTINGS)
    
    # Устанавливаем этот монитор как основной
    result = win32api.ChangeDisplaySettingsEx(device_name, devmode, win32con.CDS_SET_PRIMARY)

    if result == win32con.DISP_CHANGE_SUCCESSFUL:
        print(f"    ✅ Основной монитор изменен на {device_name}")
        # Применяем изменения
        result = win32api.ChangeDisplaySettingsEx(None, None, win32con.CDS_RESET)
        if result == win32con.DISP_CHANGE_SUCCESSFUL:
            print("      ✅ Изменения Основного монитора успешно применены.")
        else:
            print("      ❌ Не удалось применить изменения после смены монитора.")
    else:
        print(f"    ❌ Ошибка смены основного дисплея: {result}")

def switch_primary_monitor():
    """ Переключает основной монитор между двумя дисплеями с учетом координат """
    primary_display, secondary_display, monitors_info = get_monitors()

    if secondary_display:
        # Получаем информацию о дисплеях
        primary_info = next((monitor for monitor in monitors_info if monitor['device_name'] == primary_display), None)
        secondary_info = next((monitor for monitor in monitors_info if monitor['device_name'] == secondary_display), None)

        if primary_info and secondary_info:
            print(f"\n🔄 Меняем мониторы...")

            # Сначала перемещаем неосновной монитор в (0, 0)
            set_display_position(secondary_display, 0, 0)

            # Переключаем основной монитор на второй
#            time.sleep(1)  # Задержка для стабильности
            set_primary_monitor(secondary_display)

            # Теперь основной монитор смещаем, чтобы освободить место
            # Если основной был слева, сдвигаем его вправо, если справа - влево
            if secondary_info['x'] < 0:
                new_primary_x = secondary_info['width']  # Сдвигаем вправо
            else:
                new_primary_x = -secondary_info['width']  # Сдвигаем влево

            set_display_position(primary_display, new_primary_x, primary_info['y'])
    else:
        print("❌ Второй монитор не найден!")



if __name__ == "__main__":
    switch_primary_monitor()
