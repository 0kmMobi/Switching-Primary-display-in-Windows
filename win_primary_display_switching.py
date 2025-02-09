import win32api
import win32con
import time

# Определяем константы (их нет в win32con)
DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

def get_monitors():
    print("Получаем параметры всех активных мониторов и определяем 'Главный'")
    primary_display = None
    secondary_display = None
    device_index = 0
    monitors_info = []

    while True:
        try:
            device = win32api.EnumDisplayDevices(None, device_index)
            if device.StateFlags & DISPLAY_DEVICE_ACTIVE:
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

                print(f"  🖥 Монитор #{device_index+1}: {device.DeviceName}"
                    f" ({devmode.Position_x},{devmode.Position_y})"
                    f" / Флаги: {device.StateFlags:08x}"
                    f"{' <- Главный' if device.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE else ''}")
                    
            device_index += 1
        except win32api.error:
            break  # Больше дисплеев нет

    return primary_display, secondary_display, monitors_info

def change_monitor_settings(device_name, newX, newY, willBePrimary) -> bool:
    devmode = win32api.EnumDisplaySettings(device_name, win32con.ENUM_CURRENT_SETTINGS)
    print(f"  🛠 Для {device_name} меняем положение с ({devmode.Position_x}, {devmode.Position_y}) на ({newX}, {newY})")

    devmode.Position_x = newX
    devmode.Position_y = newY

    stateFlags = win32con.CDS_NORESET | win32con.CDS_UPDATEREGISTRY
    if willBePrimary:
        print(f"    + установливаем как 'Главный' монитор")
        stateFlags = stateFlags | win32con.CDS_SET_PRIMARY

    result = win32api.ChangeDisplaySettingsEx(device_name, devmode, stateFlags)
    if result == win32con.DISP_CHANGE_SUCCESSFUL:
        print(f"    ✅ Изменения успешно выполнены для {device_name}")
    else:
        print(f"    ❌ Ошибка изменений для {device_name}")

    return result == win32con.DISP_CHANGE_SUCCESSFUL


def apply_all_changes():
    print()
    result = win32api.ChangeDisplaySettingsEx()
    if result == win32con.DISP_CHANGE_SUCCESSFUL:
        print("✅ Все изменения успешно применены")
    else:
        print("❌ Ошибка применения изменений")


def switch_primary_monitor():
    """ Переключает Главный монитор между двумя найденнемы с учетом X-координаты """
    primary_display, secondary_display, monitors_info = get_monitors()

    if secondary_display:
        # Получаем информацию о дисплеях
        primary_info = next((monitor for monitor in monitors_info if monitor['device_name'] == primary_display), None)
        secondary_info = next((monitor for monitor in monitors_info if monitor['device_name'] == secondary_display), None)

        if primary_info and secondary_info:
            print(f"\n🔄 Меняем мониторы...")

            # Сначала перемещаем Неглавный монитор в (0, 0) и делаем его Главным
            if change_monitor_settings(secondary_display, 0, 0, True):
                # Бывший Главный монитор смещаем, чтобы освободить место
                # Если Главный был слева, сдвигаем его вправо, если справа - влево
                if secondary_info['x'] < 0:
                    new_primary_x = secondary_info['width']  # Сдвигаем вправо
                else:
                    new_primary_x = -secondary_info['width']  # Сдвигаем влево

                if change_monitor_settings(primary_display, new_primary_x, 0, False):
                    apply_all_changes()
    else:
        print("❌ Второй монитор не найден!")


if __name__ == "__main__":
    switch_primary_monitor()
