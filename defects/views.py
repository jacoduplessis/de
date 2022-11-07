from django.shortcuts import render


def index(request):
    return render(request, 'defects/index.html')


def notifications_list(request):
    context = {
        'notifications': [
            {
                "section": "UG2 #2",
                "section_engineer_name": "Kevin Neil Woods",
                "date": "2021-11-02",
                "equipment_name": "Thickener",
                "description": "Thickener no 2 rake got stuck underneath walkway bridge",
                "id": "UG2_2021_28"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-20",
                "equipment_name": "Flotation",
                "description": "Milling stopped due to primary rougher discharge pumps unavailable",
                "id": "UG1_RI_2022_58"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-09-19",
                "equipment_name": "Flotation",
                "description": "440 blowers not available",
                "id": "UG2_RI_2022_31"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-19",
                "equipment_name": "Flotation",
                "description": "Milling stopped due to primary rougher feed pumps tripping",
                "id": "UG1_RI_2022_57"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-14",
                "equipment_name": "Milling",
                "description": "Primary mill feed conveyor planned maintenance overrun",
                "id": "UG1_RI_2022_56"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Leon de Kock",
                "date": "2022-09-10",
                "equipment_name": "Filters",
                "description": "Larox filter 211FL01 stopped due to damaged seam",
                "id": "Mer_RI_2022_37"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-10",
                "equipment_name": "Crushing",
                "description": "Conveyor 260CV03 stopped due to magnet belt damaged",
                "id": "UG1_RI_2022_54"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-10",
                "equipment_name": "Crushing",
                "description": "Conveyor 260CV03 stopped due tot fluid drive coupling oil leak",
                "id": "UG1_RI_2022_55"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-09-09",
                "equipment_name": "Milling",
                "description": "408ML17 stopped due to low silo level",
                "id": "UG2_RI_2022_30"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-09",
                "equipment_name": "Crushing",
                "description": "Conveyor 260CV03 stopped due 260CV01 and 260CV02 unavailable",
                "id": "UG1_RI_2022_53"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-09-08",
                "equipment_name": "Milling",
                "description": "408ML17 stopped due to low silo level",
                "id": "UG2_RI_2022_29"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-09-07",
                "equipment_name": "Crushing",
                "description": "Conveyor 260CV03 snub pulley bearing failure",
                "id": "UG1_RI_2022_52"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-09-05",
                "equipment_name": "Milling",
                "description": "408ML17 motor trtipping due to misaligned encoder",
                "id": "UG2_RI_2022_28"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Leon de Kock",
                "date": "2022-09-02",
                "equipment_name": "Filters",
                "description": "Conveyor belt 211CV01 drive gearbox failed",
                "id": "Mer_RI_2022_36"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-08-31",
                "equipment_name": "Filters",
                "description": "Larox filter stopped due to defective plates and rollers",
                "id": "Mer_RI_2022_35"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Kevin Neil Woods",
                "date": "2022-08-25",
                "equipment_name": "Milling",
                "description": "440-FT-104 Floatation Cell Choked",
                "id": "UG2_2022_27"
            },
            {
                "section": "UG2 #2",
                "section_engineer_name": "Kevin Neil Woods",
                "date": "2022-08-23",
                "equipment_name": "Milling",
                "description": "Planned shutdown overrun",
                "id": "UG2_2022_26"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-08-21",
                "equipment_name": "Compressor",
                "description": "Larox filters offline due to the compressor being offline",
                "id": "Mer_RI_2022_34"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-08-20",
                "equipment_name": "Filters",
                "description": "Larox filter 602 stopped due to pump 211PP10 unavailable",
                "id": "Mer_RI_2022_32"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-08-20",
                "equipment_name": "Filters",
                "description": "Larox filter 601 stopped due toa damaged QAC",
                "id": "Mer_RI_2022_33"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-08-19",
                "equipment_name": "Pump",
                "description": "Primary mill stopped due to mill discharge pumps unavailable",
                "id": "UG1_RI_2022_51"
            },
            {
                "section": "UG2 #1",
                "section_engineer_name": "Chris Pieterse",
                "date": "2022-08-18",
                "equipment_name": "Milling",
                "description": "Planned plant shutdown overrun",
                "id": "UG1_RI_2022_50"
            },
            {
                "section": "Merensky",
                "section_engineer_name": "Adriaan van Zanten",
                "date": "2022-08-18",
                "equipment_name": "filters",
                "description": "Larox filter 601 stopped due to a leaking valve (V07)",
                "id": "Mer_RI_2022_30"
            }
        ]
    }

    return render(request, 'defects/notification_list.html', context)
