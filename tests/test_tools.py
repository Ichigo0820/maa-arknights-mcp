"""Tests for tools modules"""

import pytest
from unittest.mock import patch, MagicMock
from maa_arknights_mcp.cli import MAACLI, CLIResult
from maa_arknights_mcp.tools.game import GameTools
from maa_arknights_mcp.tools.combat import CombatTools
from maa_arknights_mcp.tools.roguelike import RoguelikeTools
from maa_arknights_mcp.tools.infrastructure import InfrastructureTools
from maa_arknights_mcp.tools.recruit import RecruitTools


class TestGameTools:
    """Test GameTools class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_startup(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Game started",
            stderr="",
            command="maa startup Official",
        )
        cli = MAACLI()
        game = GameTools(cli)
        result = game.startup(client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_closedown(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Game closed",
            stderr="",
            command="maa closedown Official",
        )
        cli = MAACLI()
        game = GameTools(cli)
        result = game.closedown(client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_activity(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout='{"events": []}',
            stderr="",
            command="maa activity Official",
        )
        cli = MAACLI()
        game = GameTools(cli)
        result = game.activity(client="Official")
        assert result.success is True


class TestCombatTools:
    """Test CombatTools class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_fight(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Fight completed",
            stderr="",
            command="maa fight BB-7",
        )
        cli = MAACLI()
        combat = CombatTools(cli)
        result = combat.fight(stage="BB-7", count=3)
        assert result.success is True
        mock_run.assert_called_once_with(
            ["fight", "BB-7", "--times", "3"], timeout=None
        )

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_fight_with_medicine_and_addr(self, mock_run):
        """理智药和 ADB 地址必须使用 maa-cli 支持的参数"""
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="", stderr="")
        cli = MAACLI()
        combat = CombatTools(cli)
        combat.fight(stage="1-7", count=0, medicine=2, series=1, addr="127.0.0.1:5555")
        mock_run.assert_called_once_with(
            [
                "fight",
                "1-7",
                "-m",
                "2",
                "--series",
                "1",
                "-a",
                "127.0.0.1:5555",
            ],
            timeout=None,
        )

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_fight_with_expiring_medicine(self, mock_run):
        """临期理智药必须映射到 maa-cli 支持的参数"""
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="", stderr="")
        cli = MAACLI()
        combat = CombatTools(cli)
        combat.fight(
            stage="AP-5", count=0, medicine=99, expiring_medicine=99
        )
        mock_run.assert_called_once_with(
            [
                "fight",
                "AP-5",
                "-m",
                "99",
                "--expiring-medicine",
                "99",
            ],
            timeout=None,
        )

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_copilot(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Copilot executed",
            stderr="",
            command="maa copilot maa://xxx",
        )
        cli = MAACLI()
        combat = CombatTools(cli)
        result = combat.copilot(maa_uris="maa://xxx")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_sscopilot(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="SS Copilot executed",
            stderr="",
            command="maa sscopilot maa://xxx",
        )
        cli = MAACLI()
        combat = CombatTools(cli)
        result = combat.sscopilot(maa_uri="maa://xxx")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_paradoxcopilot(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Paradox Copilot executed",
            stderr="",
            command="maa paradoxcopilot maa://xxx",
        )
        cli = MAACLI()
        combat = CombatTools(cli)
        result = combat.paradoxcopilot(maa_uris="maa://xxx")
        assert result.success is True


class TestRoguelikeTools:
    """Test RoguelikeTools class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_roguelike(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Roguelike started",
            stderr="",
            command="maa roguelike Phantom",
        )
        cli = MAACLI()
        roguelike = RoguelikeTools(cli)
        result = roguelike.roguelike(theme="Phantom")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_reclamation(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Reclamation started",
            stderr="",
            command="maa reclamation Tales",
        )
        cli = MAACLI()
        roguelike = RoguelikeTools(cli)
        result = roguelike.reclamation(theme="Tales")
        assert result.success is True


class TestInfrastructureTools:
    """Test InfrastructureTools class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_infrast_manage(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Infrastructure managed",
            stderr="",
            command="maa infrast manage Official",
        )
        cli = MAACLI()
        infrast = InfrastructureTools(cli)
        result = infrast.infrast_manage(client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_infrast_production(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Production started",
            stderr="",
            command="maa infrast production Official",
        )
        cli = MAACLI()
        infrast = InfrastructureTools(cli)
        result = infrast.infrast_production(client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_infrast_switch(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Operator switched",
            stderr="",
            command="maa infrast switch OperatorName power",
        )
        cli = MAACLI()
        infrast = InfrastructureTools(cli)
        result = infrast.infrast_switch(operator="OperatorName", room="power")
        assert result.success is True


class TestRecruitTools:
    """Test RecruitTools class"""

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_recruit_get(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout='{"results": []}',
            stderr="",
            command="maa recruit get Official",
        )
        cli = MAACLI()
        recruit = RecruitTools(cli)
        result = recruit.recruit_get(client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_recruit_start(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Recruit started",
            stderr="",
            command="maa recruit start Official",
        )
        cli = MAACLI()
        recruit = RecruitTools(cli)
        result = recruit.recruit_start(time=7200, client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_recruit_collect(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="Recruit collected",
            stderr="",
            command="maa recruit collect 0 Official",
        )
        cli = MAACLI()
        recruit = RecruitTools(cli)
        result = recruit.recruit_collect(index=0, client="Official")
        assert result.success is True

    @patch("maa_arknights_mcp.cli.MAACLI.run")
    def test_recruit_all(self, mock_run):
        mock_run.return_value = MagicMock(
            success=True,
            returncode=0,
            stdout="All recruits collected",
            stderr="",
            command="maa recruit all Official",
        )
        cli = MAACLI()
        recruit = RecruitTools(cli)
        result = recruit.recruit_all(client="Official")
        assert result.success is True
