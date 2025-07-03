from src.state.pokestate import BattleState, PokemonState, MoveState, TeamState
import src.state.gen1_moves

def create_example_battle_state(
        active_p1_name = None,
        active_p2_name = None
    ) -> BattleState:
    """Create an example battle state for testing."""
    
    # Create example moves
    move1 = MoveState(known=True, name="Tackle", pp=20, pp_max=20, disabled=False)
    move2 = MoveState(known=True, name="Thunderbolt", pp=15, pp_max=15, disabled=False)
    
    # Create example Pokemon
    player_pokemon = PokemonState(
        active=True,
        known=True,
        name=active_p1_name if active_p1_name else "Pikachu",
        species="Pikachu",
        type1="Electric",
        hp=85.0,
        move1=move1,
        move2=move2
    )
    
    opponent_pokemon = PokemonState(
        active=True,
        known=True,
        name=active_p2_name if active_p2_name else "Charmander",
        species="Charmander",
        type1="Fire",
        hp=90.0,
        move1=move1
    )

    opponent_bench_pokemon = PokemonState(
        active=False,
        known=False,
        name="SquadGoals",
        species="Squirtle",
        type1="Water",
        hp=100.0,
    )
    
    # Create teams
    player_team = TeamState(pk_list=[player_pokemon] + [PokemonState() for _ in range(5)])
    opponent_team = TeamState(pk_list=[opponent_pokemon, opponent_bench_pokemon] + [PokemonState() for _ in range(5)])
    
    return BattleState(
        player_active_mon=0,
        opponent_active_mon=0,
        player_team=player_team,
        opponent_team=opponent_team
    )

def create_move_state(
    name: str
):
    move = src.state.gen1_moves.get_move_by_name(name)
    if move is None:
        raise ValueError(f"Move '{name}' not found in gen1 moves.")
    return MoveState(
        known=True,
        name=move.name,
        pp=move.pp,
        pp_max=move.pp,
        disabled=False
    )