use std::{ops::Add, slice::Iter};

use pyo3::prelude::*;

use crate::{Position, WorldError};

#[pyclass]
#[derive(Clone, PartialEq, PartialOrd, Eq, Ord)]
pub enum Action {
    North,
    South,
    East,
    West,
    Stay,
}

#[pymethods]
impl Action {
    pub fn delta(&self) -> (i32, i32) {
        match self {
            Action::North => (-1, 0),
            Action::South => (1, 0),
            Action::East => (0, 1),
            Action::West => (0, -1),
            Action::Stay => (0, 0),
        }
    }
}

impl Action {
    pub fn iter() -> Iter<'static, Action> {
        [
            Action::North,
            Action::South,
            Action::East,
            Action::West,
            Action::Stay,
        ]
        .iter()
    }
}

impl From<u32> for Action {
    fn from(value: u32) -> Self {
        match value {
            0 => Action::North,
            1 => Action::South,
            2 => Action::East,
            3 => Action::West,
            4 => Action::Stay,
            _ => panic!("Invalid value for action: {}", value),
        }
    }
}

impl From<&str> for Action {
    fn from(value: &str) -> Self {
        match value {
            "North" | "N" => Action::North,
            "South" | "S" => Action::South,
            "East" | "E" => Action::East,
            "West" | "W" => Action::West,
            "Stay" => Action::Stay,
            _ => panic!("Invalid value for action: {}", value),
        }
    }
}

impl Add<&Action> for &Position {
    type Output = Result<Position, WorldError>;

    fn add(self, rhs: &Action) -> Self::Output {
        let (dx, dy) = rhs.delta();
        let x = self.0 as i32 + dx;
        let y = self.1 as i32 + dy;

        if x < 0 || y < 0 {
            return Err(WorldError::InvalidPosition { x, y });
        }
        Ok((x as usize, y as usize))
    }
}

impl Add<Position> for Action {
    type Output = Result<Position, WorldError>;

    fn add(self, rhs: Position) -> Self::Output {
        &rhs + &self
    }
}

impl Add<&Position> for &Action {
    type Output = Result<Position, WorldError>;

    fn add(self, rhs: &Position) -> Self::Output {
        rhs + self
    }
}
