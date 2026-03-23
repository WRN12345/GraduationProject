"""
@Created on : 2026.3.23
@Author: wrn
@Des: 热度算法 V2 计算器 - 针对开发者技术社区调优
维度：净票数 / 评论数 / 收藏数 / 时间衰减 / 置顶加分 / 精华加分
适用于帖子、社区、用户三种场景
"""
import math
from datetime import datetime, timezone
from typing import Optional


class HotScoreCalculator:
    """
    热度分计算器 —— 全部使用 log₁₀ 压缩，避免头部效应。

    核心设计原则：
    1. log 压缩：原始数值取 log₁₀，防止高赞帖碾压小众好内容
    2. 符号保留：踩 > 赞时投票分为负，帖子自然下沉
    3. 时间衰减：log(1+hours) 曲线，发布初期衰减快、后期趋缓
    4. 收藏(2.0) > 评论(1.2) > 投票(1.0)：权重反映用户意图强度
    5. 编辑干预：置顶/精华固定加分，覆盖有机热度
    """

    def __init__(self, settings):
        self.vote_weight = getattr(settings, "HOT_VOTE_WEIGHT", 1.0)
        self.comment_weight = getattr(settings, "HOT_COMMENT_WEIGHT", 1.2)
        self.fav_weight = getattr(settings, "HOT_FAV_WEIGHT", 2.0)
        self.time_decay = getattr(settings, "HOT_TIME_DECAY", 1.8)
        self.pin_bonus = getattr(settings, "HOT_PIN_BONUS", 5.0)
        self.featured_bonus = getattr(settings, "HOT_FEATURED_BONUS", 2.0)
        # 基准分数，确保热度不会变成负数
        self.base_score = getattr(settings, "HOT_BASE_SCORE", 5.0)

    # ──────────────────────────────────────────
    # 1. 帖子热度
    # ──────────────────────────────────────────
    def post_score(
        self,
        upvotes: int,
        downvotes: int,
        comment_count: int,
        favorite_count: int,
        created_at: Optional[datetime] = None,
        is_pinned: bool = False,
        is_featured: bool = False,
    ) -> float:
        """
        帖子热度公式（log₁₀）：

            vote_score    = sign(net) × log(max(1, |up−down|)) × 1.0
            comment_score = log(1 + comments)  × 1.2
            fav_score     = log(1 + favorites) × 2.0
            time_decay    = −1.8 × log(1 + hours_since_created)
            pin_bonus     = is_pinned   × 5.0
            featured_bonus= is_featured × 2.0

            total = vote_score + comment_score + fav_score
                  + time_decay + pin_bonus + featured_bonus

        置顶加分(+5.0)可确保置顶帖压过任何有机热度（正常热帖总分约3~8）。
        精华加分(+2.0)约等于额外获得100个收藏的加成。
        """
        net = upvotes - downvotes
        sign = 1 if net >= 0 else -1
        vote_score = sign * math.log10(max(1, abs(net))) * self.vote_weight
        comment_score = math.log10(1 + comment_count) * self.comment_weight
        fav_score = math.log10(1 + favorite_count) * self.fav_weight

        hours = self._hours_since(created_at)
        time_penalty = -self.time_decay * math.log10(1 + hours)

        pin_bonus = self.pin_bonus if is_pinned else 0.0
        featured_bonus = self.featured_bonus if is_featured else 0.0

        # 加上基准分数，确保热度不会变成负数
        total = vote_score + comment_score + fav_score + time_penalty + pin_bonus + featured_bonus + self.base_score

        return round(total, 7)

    # ──────────────────────────────────────────
    # 2. 社区热度（成员、帖子、近期活跃）
    # ──────────────────────────────────────────
    def community_score(
        self,
        member_count: int,
        post_count: int,
        posts_7d: int,
        comments_7d: int = 0,
        created_at: Optional[datetime] = None,
    ) -> float:
        """
        社区热度公式：

            member_score   = min(log(members), 5)
            post_score     = min(log(1 + posts), 5)
            activity_score = min(log(1 + posts_7d) × 1.5 + log(1 + comments_7d) × 0.8, 4)
            age_bonus      = max(0, 2 - decay × log(1 + days_old))   # 新社区加分

            total = member_score + post_score + activity_score + age_bonus
        """
        member_score = min(math.log10(max(1, member_count)), 5)
        post_score_val = min(math.log10(1 + post_count), 5)
        activity_score = min(
            math.log10(1 + posts_7d) * 1.5 + math.log10(1 + comments_7d) * 0.8,
            4,
        )

        days = self._hours_since(created_at) / 24
        age_bonus = max(0.0, 2.0 - self.time_decay * math.log10(1 + days))

        # 加上基准分数，确保热度不会变成负数
        total = member_score + post_score_val + activity_score + age_bonus + self.base_score

        return round(total, 7)

    # ──────────────────────────────────────────
    # 3. 用户活跃度
    # ──────────────────────────────────────────
    def user_score(
        self,
        karma: int,
        post_count: int,
        comment_count: int,
        activity_7d: int,
        last_login_at: Optional[datetime] = None,
    ) -> float:
        """
        用户活跃度公式：

            karma_score    = min(log(max(1, karma)), 6)
            content_score  = min(log(1 + posts + comments), 3)
            activity_score = min(log(1 + activity_7d) × 0.8, 2.5)
            login_bonus    = max(0, 1.5 - decay × log(1 + hours_since_login))

            total = karma_score + content_score + activity_score + login_bonus
        """
        karma_score = min(math.log10(max(1, karma)), 6)
        content_score = min(math.log10(1 + post_count + comment_count), 3)
        activity_score = min(math.log10(1 + activity_7d) * 0.8, 2.5)

        login_hours = self._hours_since(last_login_at)
        login_bonus = max(0.0, 1.5 - self.time_decay * 0.5 * math.log10(1 + login_hours))

        # 加上基准分数，确保热度不会变成负数
        total = karma_score + content_score + activity_score + login_bonus + self.base_score

        return round(total, 7)

    # ──────────────────────────────────────────
    # 工具方法
    # ──────────────────────────────────────────
    @staticmethod
    def _hours_since(dt: Optional[datetime]) -> float:
        """返回距离 dt 的小时数；dt 为 None 时返回 0"""
        if dt is None:
            return 0.0
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = now - dt
        return max(0.0, delta.total_seconds() / 3600)


# 导出
__all__ = ["HotScoreCalculator"]
