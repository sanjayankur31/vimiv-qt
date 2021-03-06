Feature: Push messages to the statusbar.

    Background:
        Given I open any directory

    Scenario: Display warning message.
        When I log the warning 'this is a warning'
        Then the message
            'this is a warning'
            should be displayed

    Scenario: Display message when bar is hidden
        When I run set statusbar.show false
        And I log the warning 'this is a warning'
        Then the message
            'this is a warning'
            should be displayed
        And the bar should be visible

    Scenario: Hide statusbar after message
        When I run set statusbar.show false
        And I log the warning 'this is a warning'
        And I clear the status
        Then the bar should not be visible

    Scenario: Clear message after key press
        When I log the warning 'this is a warning'
        And I press 0
        Then no message should be displayed
