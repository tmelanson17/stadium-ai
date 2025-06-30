from enum import Enum

# from src.state.pokestate import BattleState

class Messages(Enum):
    NOTVERY = "It's not very effective..."
    SUPER = "It's super effective!"
    SWITCH1 = "OK! Come back!"
    SWITCH2 = "Enough! Come back!"
    CRIT = "Critical hit!"
    MISS = "Its attack missed!"
    DIG = "It dug a hole!"
    FLY = "It flew up high!"
    CONF = "It's confused!"
    SELFHIT = "It attacked itself!"
    SUCK = "It sucked HP!"
    STATUSBRN = "Burnburnburn" # TODO: What is the actual message
    STARTCONF = "It became confused!"
    STARTFRZ = "It was frozen solid!"
    STARTPLZ = "It may not attack!"
    STARTPSN = "It's badly poisoned!"
    STARTBRN = "It was burned!" 
    STARTSLP = "It fell asleep!"
    STATUSFAIL = "But, it failed!"
    PLZ = "It's fully paralyzed!"
    FRZ = "It's frozen solid!"
    SLP = "It's fast asleep!"
    REST = "It fell asleep and was healed!"
    RECOVER = "It regained health!"
    WOKE = "It woke up!" # TODO: Double check this one
    NOCONF = "It's no longer confused!"
    ATK_G_INC = "ATTACK greatly increased!"
    DEF_G_INC = "DEFENSE greatly increased!"
    SPC_G_INC = "SPECIAL greatly increased!"
    SPD_G_INC = "SPEED greatly increased!"
    ATK_INC = "ATTACK increased!"
    DEF_INC = "DEFENSE increased!"
    SPC_INC = "SPECIAL increased!"
    SPD_INC = "SPEED increased!"
    SPECIAL_DOWN = "SPECIAL fell!"
    SPEED_DOWN = "SPEED fell!"
    DEFENSE_DOWN = "DEFENSE fell!"
    ATTACK_DOWN = "ATTACK fell!"

def is_update_message(message: Messages) -> bool:
    """
    Check if the message is a condition-related message.
    
    Args:
        message: The message string to check.
        
    Returns:
        True if the message is a condition-related message, False otherwise.
    """
    return message in [
        Messages.ATK_G_INC,
        Messages.ATK_INC,
        Messages.ATTACK_DOWN,
        Messages.DEF_G_INC,
        Messages.DEF_INC,
        Messages.DEFENSE_DOWN,
        Messages.SPC_G_INC,
        Messages.SPC_INC,
        Messages.SPECIAL_DOWN,
        Messages.SPD_G_INC,
        Messages.SPD_INC,
        Messages.SPEED_DOWN,
        Messages.STARTBRN,
        Messages.STARTCONF,
        Messages.STARTFRZ,
        Messages.STARTPLZ,
        Messages.STARTPSN,
        Messages.WOKE,
        Messages.DIG,
        Messages.FLY,
        Messages.REST,
    ]