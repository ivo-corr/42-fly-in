*This project has been created as part of the 42 curriculum by icorrale.*

*This project has been created as part of the 42 curriculum by <login1>, <login2>.*

# 42's Fly In

## Description

This project consists of designing an efficient drone routing system that navigates multiple drones through connected zones while minimizing simulation turns and handling movement constraints.

### How It Works

[Explain the general concept and workflow of the application.]

[Describe what the user provides as input and what the program produces as output.]

---

## Instructions

### Prerequisites

No special packages are required, only flake8 and mypy to check correct formatting.

### Installation

```git clone https://github.com/ivo-corr/42-fly-in.git [or vogsphere link]```

```cd 42-fly-in```

```make run```

or

```make run-map MAP='easy/edge_case.txt'```

### Usage

Once in the terminal UI pick the map you want to simulate from the ```/maps``` directory or run a specific map directly
```make run-map MAP=[map_name]```

---

## Algorithm and Implementation Strategy

#### Algorithm Choice

The algorithm is not an implementation of a known algorithm to the extent that I know, it was implemented in a way that i thought made sense and it turned out to be benchmark compliant so I didn't need to change it.

#### Description

                 ┌──────────────────────┐
                 │      next_turn()     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ for each d in each z │
                 │ possible_moves() and │
                 │      hasPath()       │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 │                      │
                 ▼                      ▼
       ┌─────────────────┐    ┌─────────────────┐
       │      move()     │    │do not move drone│
       └─────────────────┘    └─────────────────┘
In each turn we iterate through every zone in an outer loop, which makes my algorithm a locally optimized greedy algorithm, and every drone in each zone in an inner loop. For each drone we compute possible moves forward using the function ```possible_moves()``` that belongs to the class ```Zone``` that the drone is occupying at a given time. We categorize all possible moves for the zone into each of the zone types: ```PRIORITY```, ```NORMAL```, ```RESTRICTED```, for each of them filtering out zones that would make the path to the goal longer or equal to what it currently is, necessarily shortening the path each move (this is ensured with the beautiful recursive function ```hasPath```). The choice of the next move is then made according to the first best option: if the PRIORITY set is empty then check the NORMAL set, if normal is empty then go with first element in the RESTRICTED set, if everything is empty then don't move, there is no possible move in this turn for this drone.

#### Implementation

```possible_moves()```: 

```hasPath()```:


### Technical Challenges

My class structure initially was comprised of nested classes, which made the code less readable and difficult to update so I restructured it to a cleaner format mid-project. The rendering in terminal took me longer than it should have because I did not want to look for already existing algorithms for things i needed, in the end I implemented Bresenham's algorithm for connecting any two arbitrary points in my grid because I couldn't come up with the solution myself.

---

## Visual Representation

### Overview

I picked a terminal based GUI for this project, which I regret because it took me longer than it would've taken with a graphics library like pygame or similar.


### User Experience

The terminal UI is comprised of a grey map, zones are represented inside of it in the form of rectangles with integers in them, the integers represent the number of drones in the zone. When drones are transiting a connection toward a restricted zone they are represented with their names, e.g 'D0', 'D1' next to their respective connections. Animations were omited outside of this.

### Technical Implementation

No libraries are needed to run fly-in.

---

### AI Usage

LLMs were used primarily for conceptual clarification. No code in this project was generated with AI.
AI was used to help with README file and comments that comply with the standard required by the subject.
