function buildEntityPacket(character, category = "CharCreateUI") {
    const [
        name,
        class_name,
        level,
        computed,
        extra1,
        extra2,
        extra3,
        extra4,
        hair_color,
        skin_color,
        shirt_color,
        pant_color,
        equipped_gear,
    ] = character;

    // Set parent in correct format
    let parent;
    if (category === "CharCreateUI") {
        parent = `CharCreateUI:Starter${class_name}`;
    } else {
        parent = `${category}:${class_name}`;
    }

    // Check for empty values
    const computedVal = computed || "Male";
    const extra1Val = extra1 || "Head01";
    const extra2Val = extra2 || "Hair01";
    const extra3Val = extra3 || "Mouth01";
    const extra4Val = extra4 || "Face01";

    // Create XML
    const xml = `<EntType EntName='PaperDoll' parent='${parent}'>
        <Level>${level}</Level>
        <Name>${name}</Name>
        <HairColor>${hair_color}</HairColor>
        <SkinColor>${skin_color}</SkinColor>
        <ShirtColor>${shirt_color}</ShirtColor>
        <PantColor>${pant_color}</PantColor>
        <GenderSet>${computedVal}</GenderSet>
        <HeadSet>${extra1Val}</HeadSet>
        <HairSet>${extra2Val}</HairSet>
        <MouthSet>${extra3Val}</MouthSet>
        <FaceSet>${extra4Val}</FaceSet>
        <CustomScale>${
            class_name.toLowerCase() === "mage" ? 0.8 : 1.0
        }</CustomScale>
        <EquippedGear>
            ${equipped_gear || ""}
        </EquippedGear>
    </EntType>`
        .replace(/\n/g, "")
        .replace(/    /g, "");

    return xml;
}

export { buildEntityPacket };
