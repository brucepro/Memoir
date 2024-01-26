"""Goals system

"""

import pathlib
import sqlite3




class Goal:
    def __init__(self, title, description, importance_rating, deadline=None, status="incomplete", parent_id=None, reason="", success_criteria=""):
        self.title = title
        self.description = description
        self.importance_rating = importance_rating
        self.deadline = deadline if deadline else None
        self.status = status
        self.parent_id = parent_id
        self.reason = reason
        self.success_criteria = success_criteria

    def add(self, db):
        cursor = db.cursor()
        query = "INSERT INTO goals (title, description, importance_rating, deadline, status, parent_id, reason, success_criteria) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        values = (self.title, self.description, self.importance_rating, self.deadline, self.status, self.parent_id, self.reason, self.success_criteria)
        cursor.execute(query, values)
        db.commit()

    def delete(db, goal_id):
        cursor = db.cursor()
        query = "DELETE FROM goals WHERE id=?"
        values = (goal_id, )
        cursor.execute(query, values)
        db.commit()

    def update_goal(db, goal_id, status):
        """
        This function updates the status of a specific goal in the SQLite database.

        Args:
            db (sqlite3.Connection): The SQLite database connection object.
            goal_id (int): The ID of the goal to be updated.
            status (str): The new status for the goal ('incomplete' or 'complete').

        Returns:
            None

        Side Effects:
            Modifies the database by updating the corresponding goal's status.
        """
        # Check if the goal_id exists in the database
        cursor = db.cursor()
        query = "SELECT * FROM goals WHERE id=?"
        cursor.execute(query,(goal_id))
        result = cursor.fetchone()

        if not result:
            raise ValueError("Goal ID does not exist")

        # Update the status of the specified goal in the database
        query = "UPDATE goals SET status=? WHERE id=?"
        cursor.execute(query, (status, goal_id))
        db.commit()

    @classmethod
    def recall_by_title(cls, db, title):
        cursor = db.cursor()
        query = "SELECT * FROM goals WHERE title=?"
        values = (title, )
        cursor.execute(query, values)
        return [Goal(*row) for row in cursor.fetchall()]
    
    @classmethod
    def recall_by_id(cls, db, id):
        cursor = db.cursor()
        query = "SELECT * FROM goals WHERE id=?"
        values = (id, )
        cursor.execute(query, values)
        return [Goal(*row) for row in cursor.fetchall()]
    
    @classmethod
    def list_nested_goals(cls, db, goal):
        nested_goals = []

        if not isinstance(goal, Goal):
            raise ValueError("Invalid argument: expected a 'Goal' instance")

        cursor = db.cursor()
        query = "SELECT * FROM goals WHERE parent_id=?"
        values = (goal.id, )
        cursor.execute(query, values)

        for row in cursor.fetchall():
            nested_goals.append(Goal(*row))

        return nested_goals

    @classmethod
    def list_current_goals_ordered_by_importance(cls, db):
        cursor = db.cursor()
        query = "SELECT * FROM goals WHERE status='incomplete' OR status='in_progress' ORDER BY importance_rating DESC"
        cursor.execute(query)
        all_goals = str(cursor.fetchall())
        return all_goals
