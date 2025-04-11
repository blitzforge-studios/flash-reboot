def build_entity_packet(character, category="CharCreateUI"):
    (name, class_name, level, computed, extra1, extra2, extra3, extra4,
     hair_color, skin_color, shirt_color, pant_color, equipped_gear) = character
    
    # Parent'ı doğru formatta ayarla
    if category == "CharCreateUI":
        parent = f"CharCreateUI:Starter{class_name}"
    else:
        parent = f"{category}:{class_name}"
    
    # Boş değerleri kontrol et
    computed = computed if computed else "Male"
    extra1 = extra1 if extra1 else "Head01"
    extra2 = extra2 if extra2 else "Hair01"
    extra3 = extra3 if extra3 else "Mouth01"
    extra4 = extra4 if extra4 else "Face01"
    
    # XML oluştur
    xml = f"""<EntType EntName='PaperDoll' parent='{parent}'>
        <Level>{level}</Level>
        <Name>{name}</Name>
        <HairColor>{hair_color}</HairColor>
        <SkinColor>{skin_color}</SkinColor>
        <ShirtColor>{shirt_color}</ShirtColor>
        <PantColor>{pant_color}</PantColor>
        <GenderSet>{computed}</GenderSet>
        <HeadSet>{extra1}</HeadSet>
        <HairSet>{extra2}</HairSet>
        <MouthSet>{extra3}</MouthSet>
        <FaceSet>{extra4}</FaceSet>
        <CustomScale>{0.8 if class_name.lower() == 'mage' else 1.0}</CustomScale>
        <EquippedGear>
            {equipped_gear if equipped_gear else ""}
        </EquippedGear>
    </EntType>"""
    
    return xml.replace('\n', '').replace('    ', '')