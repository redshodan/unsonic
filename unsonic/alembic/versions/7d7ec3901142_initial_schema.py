"""Initial schema

Revision ID: 7d7ec3901142
Revises:
Create Date: 2017-04-08 16:03:25.287910

"""
from alembic import op
import sqlalchemy as sa
from unsonic.auth import Roles


# revision identifiers, used by Alembic.
revision = '7d7ec3901142'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    # DBInfo
    op.create_table(
        'un_dbinfo',
        sa.Column('version', sa.String(length=32), nullable=False),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('version', name=op.f('pk_un_dbinfo'))
        )

    # Users
    users_t = op.create_table(
        'un_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('password', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('maxbitrate', sa.Integer(), nullable=False),
        sa.Column('scrobble_user', sa.Text(), nullable=True),
        sa.Column('scrobble_pass', sa.Text(), nullable=True),
        sa.Column('scrobble_type',
                  sa.Enum('NONE', 'LAST_FM', 'LIBRE_FM', name='scrobble_types'),
                  nullable=False),
        sa.Column('playqueue_cur', sa.Integer(), nullable=True),
        sa.Column('playqueue_pos', sa.Integer(), nullable=False),
        sa.Column('playqueue_mtime', sa.DateTime(), nullable=True),
        sa.Column('playqueue_mby', sa.Text(), nullable=True),
        sa.Column('avatar', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['avatar'], ['images.id'],
                                name=op.f('fk_un_users_avatar_images')),
        sa.ForeignKeyConstraint(['playqueue_cur'], ['tracks.id'],
                                name=op.f('fk_un_users_playqueue_cur_tracks')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_users')),
        sa.UniqueConstraint('name', name=op.f('uq_un_users_name'))
        )

    # AlbumRatings
    op.create_table(
        'un_albumratings',
        sa.Column('album_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('pseudo_rating', sa.Boolean(name='pseudo_rating'),
                  nullable=False),
        sa.Column('starred', sa.DateTime(), nullable=True),
        sa.Column('pseudo_starred', sa.Boolean(name='pseudo_starred'),
                  nullable=False),
        sa.ForeignKeyConstraint(['album_id'], ['albums.id'],
                                name=op.f('fk_un_albumratings_album_id_albums'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_albumratings_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('album_id', 'user_id',
                                name=op.f('pk_un_albumratings'))
    )

    # ArtistRatings
    op.create_table(
        'un_artistratings',
        sa.Column('artist_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('pseudo_rating', sa.Boolean(name='pseudo_rating'),
                  nullable=False),
        sa.Column('starred', sa.DateTime(), nullable=True),
        sa.Column('pseudo_starred', sa.Boolean(name='pseudo_starred'),
                  nullable=False),
        sa.ForeignKeyConstraint(
            ['artist_id'], ['artists.id'],
            name=op.f('fk_un_artistratings_artist_id_artists'),
            ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['un_users.id'],
            name=op.f('fk_un_artistratings_user_id_un_users'),
            ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('artist_id', 'user_id',
                                name=op.f('pk_un_artistratings'))
    )

    # Config
    op.create_table(
        'un_config',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('key', name=op.f('pk_un_config'))
    )

    # User Config
    op.create_table(
        'un_userconfig',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_userconfig_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'key', name=op.f('pk_un_userconfig'))
    )

    # PlayCounts
    op.create_table(
        'un_playcounts',
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'],
                                name=op.f('fk_un_playcounts_track_id_tracks'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_playcounts_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('track_id', 'user_id',
                                name=op.f('pk_un_playcounts'))
    )

    # PlayLists
    op.create_table(
        'un_playlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('public', sa.Integer(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('changed', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_playlists_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_playlists'))
    )

    # PlayQueues
    op.create_table(
        'un_playqueues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'],
                                name=op.f('fk_un_playqueues_track_id_tracks'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_playqueues_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_playqueues'))
    )

    # Roles
    roles_t = op.create_table(
        'un_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_roles_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_roles')),
        sa.UniqueConstraint('user_id', 'name', name=op.f('uq_un_roles_user_id'))
    )

    # Scrobbles
    op.create_table(
        'un_scrobbles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tstamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'],
                                name=op.f('fk_un_scrobbles_track_id_tracks'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_scrobbles_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_scrobbles'))
    )
    op.create_index('scrobble_user_index', 'un_scrobbles', ['user_id'],
                    unique=False)

    # TrackRatings
    op.create_table(
        'un_trackratings',
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('starred', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'],
                                name=op.f('fk_un_trackratings_track_id_tracks'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_trackratings_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('track_id', 'user_id',
                                name=op.f('pk_un_trackratings'))
    )

    # playlist_images
    op.create_table(
        'un_playlist_images',
        sa.Column('playlist_id', sa.Integer(), nullable=True),
        sa.Column('img_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['img_id'], ['images.id'],
            name=op.f('fk_un_playlist_images_img_id_images')),
        sa.ForeignKeyConstraint(
            ['playlist_id'], ['un_playlists.id'],
            name=op.f('fk_un_playlist_images_playlist_id_un_playlists'),
            ondelete='CASCADE')
    )

    # PlayListTracks
    op.create_table(
        'un_playlisttracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['playlist_id'], ['un_playlists.id'],
            name=op.f('fk_un_playlisttracks_playlist_id_un_playlists'),
            ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['track_id'], ['tracks.id'],
            name=op.f('fk_un_playlisttracks_track_id_tracks'),
            ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_playlisttracks'))
    )

    # PlayListUsers
    op.create_table(
        'un_playlistusers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['playlist_id'], ['un_playlists.id'],
            name=op.f('fk_un_playlistusers_playlist_id_un_playlists'),
            ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['un_users.id'],
            name=op.f('fk_un_playlistusers_user_id_un_users'),
            ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_playlistusers'))
    )

    # Prepopulate some data
    op.bulk_insert(users_t, [{"name": "admin", "maxbitrate": 0,
                              "scrobbling": True, "scrobble_type": "NONE",
                              "playqueue_pos": 0}])
    for role in Roles.admin_roles:
        op.bulk_insert(roles_t, [{"user_id": 1, "name": role}])


def downgrade():
    op.drop_table('un_playlistusers')
    op.drop_table('un_playlisttracks')
    op.drop_table('un_playlist_images')
    op.drop_table('un_trackratings')
    op.drop_index('scrobble_user_index', table_name='un_scrobbles')
    op.drop_table('un_scrobbles')
    op.drop_table('un_roles')
    op.drop_table('un_playqueues')
    op.drop_table('un_playlists')
    op.drop_table('un_playcounts')
    op.drop_table('un_config')
    op.drop_table('un_artistratings')
    op.drop_table('un_albumratings')
    op.drop_table('un_users')
    op.drop_table('un_dbinfo')
