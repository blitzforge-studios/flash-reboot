def build_entity_packet(character, category="CharCreateUI"):
    name, class_name, level, computed, extra1, extra2, extra3, extra4, hair_color, skin_color, shirt_color, pant_color, equipped_gear = character
    
    # Set parent in correct format
    if category == "CharCreateUI":
        parent = f"CharCreateUI:Starter{class_name}"
    else:
        parent = f"{category}:{class_name}"
    
    # Check for empty values
    computed_val = computed or "Male"
    extra1_val = extra1 or "Head01"
    extra2_val = extra2 or "Hair01"
    extra3_val = extra3 or "Mouth01"
    extra4_val = extra4 or "Face01"
    
    # Create XML
    xml = f"""<EntType EntName='PaperDoll' parent='{parent}'>
        <Level>{level}</Level>
        <Name>{name}</Name>
        <HairColor>{hair_color}</HairColor>
        <SkinColor>{skin_color}</SkinColor>
        <ShirtColor>{shirt_color}</ShirtColor>
        <PantColor>{pant_color}</PantColor>
        <GenderSet>{computed_val}</GenderSet>
        <HeadSet>{extra1_val}</HeadSet>
        <HairSet>{extra2_val}</HairSet>
        <MouthSet>{extra3_val}</MouthSet>
        <FaceSet>{extra4_val}</FaceSet>
        <CustomScale>{0.8 if class_name.lower() == "mage" else 1.0}</CustomScale>
        <EquippedGear>
            {equipped_gear or ""}
        </EquippedGear>
    </EntType>""".replace("\n", "").replace("    ", "")
    
    return xml