"""Message type definitions. For synchronization with the TypeScript definitions, see
`_typescript_interface_gen.py.`"""

from __future__ import annotations

import dataclasses
import uuid
from typing import Any, ClassVar, Dict, Optional, Tuple, Type, TypeVar, Union

import numpy as np
import numpy.typing as npt
from typing_extensions import Literal, override

from . import infra, theme, uplot


@dataclasses.dataclass(frozen=True)
class GuiSliderMark:
    value: float
    label: Optional[str]


LiteralColor = Literal[
    "dark",
    "gray",
    "red",
    "pink",
    "grape",
    "violet",
    "indigo",
    "blue",
    "cyan",
    "green",
    "lime",
    "yellow",
    "orange",
    "teal",
]


TagLiteral = Literal["GuiComponentMessage", "SceneNodeMessage"]


class Message(infra.Message):
    _tags: ClassVar[Tuple[TagLiteral, ...]] = tuple()

    @override
    def redundancy_key(self) -> str:
        """Returns a unique key for this message, used for detecting redundant
        messages.

        For example: if we send 1000 GUI value updates for the same GUI
        element, we should only keep the latest message.
        """
        parts = [type(self).__name__]

        # Scene node manipulation messages all have a "name" field.
        node_name = getattr(self, "name", None)
        if node_name is not None:
            parts.append(node_name)

        # GUI and notification messages all have an "uuid" field.
        node_name = getattr(self, "uuid", None)
        if node_name is not None:
            parts.append(node_name)

        return "_".join(parts)

    @classmethod
    def __init_subclass__(cls, tag: TagLiteral | None = None):
        """Tag will be used to create a union type in TypeScript."""
        super().__init_subclass__()
        if tag is not None:
            cls._tags = cls._tags + (tag,)


@dataclasses.dataclass
class _CreateSceneNodeMessage(Message, tag="SceneNodeMessage"):
    name: str

    @override
    def redundancy_key(self) -> str:
        """All scene nodes will have the same redundancy key."""
        return f"create-or-remove-scene-{self.name}"


@dataclasses.dataclass
class RemoveSceneNodeMessage(Message):
    """Remove a particular node from the scene."""

    name: str

    @override
    def redundancy_key(self) -> str:
        # This is intentionally the same as the redundancy key for
        # _CreateSceneNodeMessage: this way, when we remove a scene node the
        # message for creating the scene node will automatically be culled.
        return f"create-or-remove-scene-{self.name}"


@dataclasses.dataclass
class _CreateGuiComponentMessage(Message, tag="GuiComponentMessage"):
    uuid: str

    @override
    def redundancy_key(self) -> str:
        return f"create-or-remove-gui-{self.uuid}"


@dataclasses.dataclass
class GuiRemoveMessage(Message):
    """Sent server->client to remove a GUI element."""

    uuid: str

    @override
    def redundancy_key(self) -> str:
        # Intentionally the same as the redundancy key for
        # _CreateGuiComponentMessage.
        return f"create-or-remove-gui-{self.uuid}"


T = TypeVar("T", bound=Type[Message])


@dataclasses.dataclass
class RunJavascriptMessage(Message):
    """Message for running some arbitrary Javascript on the client.
    We use this to set up the Plotly.js package, via the plotly.min.js source
    code."""

    source: str

    @override
    def redundancy_key(self) -> str:
        # Never cull these messages.
        return str(uuid.uuid4())


@dataclasses.dataclass
class NotificationMessage(Message):
    """Notification message."""

    mode: Literal["show", "update"]
    uuid: str
    props: NotificationProps


@dataclasses.dataclass
class NotificationProps:
    title: str
    """Title of the notification. Synchronized automatically when assigned."""
    body: str
    """Body text of the notification. Synchronized automatically when assigned."""
    loading: bool
    """Whether to show a loading indicator. Synchronized automatically when assigned."""
    with_close_button: bool
    """Whether to show a close button. Synchronized automatically when assigned."""
    auto_close: Union[int, Literal[False]]
    """Time in milliseconds after which the notification should auto-close, or False to disable auto-close. Synchronized automatically when assigned."""
    color: Union[LiteralColor, Tuple[int, int, int], None]
    """Color of the notification. Synchronized automatically when assigned."""


@dataclasses.dataclass
class RemoveNotificationMessage(Message):
    """Remove a specific notification."""

    uuid: str


@dataclasses.dataclass
class ViewerCameraMessage(Message):
    """Message for a posed viewer camera.
    Pose is in the form T_world_camera, OpenCV convention, +Z forward."""

    wxyz: Tuple[float, float, float, float]
    position: Tuple[float, float, float]
    fov: float
    near: float
    far: float
    image_height: int
    image_width: int
    look_at: Tuple[float, float, float]
    up_direction: Tuple[float, float, float]


# The list of scene pointer events supported by the viser frontend.
ScenePointerEventType = Literal["click", "rect-select"]


@dataclasses.dataclass
class ScenePointerMessage(Message):
    """Message for a raycast-like pointer in the scene.
    origin is the viewing camera position, in world coordinates.
    direction is the vector if a ray is projected from the camera through the clicked pixel,
    """

    # Later we can add `double_click`, `move`, `down`, `up`, etc.
    event_type: ScenePointerEventType
    ray_origin: Optional[Tuple[float, float, float]]
    ray_direction: Optional[Tuple[float, float, float]]
    screen_pos: Tuple[Tuple[float, float], ...]


@dataclasses.dataclass
class ScenePointerEnableMessage(Message):
    """Message to enable/disable scene click events."""

    enable: bool
    event_type: ScenePointerEventType

    @override
    def redundancy_key(self) -> str:
        return (
            type(self).__name__ + "-" + self.event_type + "-" + str(self.enable).lower()
        )


@dataclasses.dataclass
class CameraFrustumMessage(_CreateSceneNodeMessage):
    """Variant of CameraMessage used for visualizing camera frustums.

    OpenCV convention, +Z forward."""

    props: CameraFrustumProps


@dataclasses.dataclass
class CameraFrustumProps:
    fov: float
    """Field of view of the camera (in radians). Synchronized automatically when assigned."""
    aspect: float
    """Aspect ratio of the camera (width over height). Synchronized automatically when assigned."""
    scale: float
    """Scale factor for the size of the frustum. Synchronized automatically when assigned."""
    line_width: float
    """Width of the frustum lines. Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the frustum as RGB integers. Synchronized automatically when assigned."""
    image_media_type: Optional[Literal["image/jpeg", "image/png"]]
    """Format of the provided image ('image/jpeg' or 'image/png'). Synchronized automatically when assigned."""
    _image_data: Optional[bytes]
    """Optional image to be displayed on the frustum. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GlbMessage(_CreateSceneNodeMessage):
    """GlTF message."""

    props: GlbProps


@dataclasses.dataclass
class GlbProps:
    glb_data: bytes
    """A binary payload containing the GLB data. Synchronized automatically when assigned."""
    scale: float
    """A scale for resizing the GLB asset. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""


@dataclasses.dataclass
class FrameMessage(_CreateSceneNodeMessage):
    """Coordinate frame message."""

    props: FrameProps


@dataclasses.dataclass
class FrameProps:
    show_axes: bool
    """Boolean to indicate whether to show the frame as a set of axes + origin sphere. Synchronized automatically when assigned."""
    axes_length: float
    """Length of each axis. Synchronized automatically when assigned."""
    axes_radius: float
    """Radius of each axis. Synchronized automatically when assigned."""
    origin_radius: float
    """Radius of the origin sphere. Synchronized automatically when assigned."""
    origin_color: Tuple[int, int, int]
    """Color of the origin sphere as RGB integers. Synchronized automatically when assigned."""


@dataclasses.dataclass
class BatchedAxesMessage(_CreateSceneNodeMessage):
    """Batched axes message.

    Positions and orientations should follow a `T_parent_local` convention, which
    corresponds to the R matrix and t vector in `p_parent = [R | t] p_local`."""

    props: BatchedAxesProps


@dataclasses.dataclass
class BatchedAxesProps:
    batched_wxyzs: npt.NDArray[np.float32]
    """Float array of shape (N,4) representing quaternion rotations. Synchronized automatically when assigned."""
    batched_positions: npt.NDArray[np.float32]
    """Float array of shape (N,3) representing positions. Synchronized automatically when assigned."""
    batched_scales: Optional[npt.NDArray[np.float32]]
    """Float array of shape (N,) or (N,3) representing uniform or per-axis (XYZ) scales. Synchronized automatically when assigned."""
    axes_length: float
    """Length of each axis. Synchronized automatically when assigned."""
    axes_radius: float
    """Radius of each axis. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GridMessage(_CreateSceneNodeMessage):
    """Grid message. Helpful for visualizing things like ground planes."""

    props: GridProps


@dataclasses.dataclass
class GridProps:
    width: float
    """Width of the grid. Synchronized automatically when assigned."""
    height: float
    """Height of the grid. Synchronized automatically when assigned."""
    width_segments: int
    """Number of segments along the width. Synchronized automatically when assigned."""
    height_segments: int
    """Number of segments along the height. Synchronized automatically when assigned."""
    plane: Literal["xz", "xy", "yx", "yz", "zx", "zy"]
    """The plane in which the grid is oriented. Synchronized automatically when assigned."""
    cell_color: Tuple[int, int, int]
    """Color of the grid cells as RGB integers. Synchronized automatically when assigned."""
    cell_thickness: float
    """Thickness of the grid lines. Synchronized automatically when assigned."""
    cell_size: float
    """Size of each cell in the grid. Synchronized automatically when assigned."""
    section_color: Tuple[int, int, int]
    """Color of the grid sections as RGB integers. Synchronized automatically when assigned."""
    section_thickness: float
    """Thickness of the section lines. Synchronized automatically when assigned."""
    section_size: float
    """Size of each section in the grid. Synchronized automatically when assigned."""
    shadow_opacity: float
    """If true, shadows are casted onto the grid plane. Synchronized automatically when assigned."""


@dataclasses.dataclass
class LabelMessage(_CreateSceneNodeMessage):
    """Add a 2D label to the scene."""

    props: LabelProps


@dataclasses.dataclass
class LabelProps:
    text: str
    """Text content of the label. Synchronized automatically when assigned."""


@dataclasses.dataclass
class Gui3DMessage(_CreateSceneNodeMessage):
    """Add a 3D gui element to the scene."""

    props: Gui3DProps


@dataclasses.dataclass
class Gui3DProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    container_uuid: str
    """Identifier for the container. Synchronized automatically when assigned."""


@dataclasses.dataclass
class PointCloudMessage(_CreateSceneNodeMessage):
    """Point cloud message.

    Positions are internally canonicalized to float32, colors to uint8.

    Float color inputs should be in the range [0,1], int color inputs should be in the
    range [0,255]."""

    props: PointCloudProps


@dataclasses.dataclass
class PointCloudProps:
    points: Union[npt.NDArray[np.float16], npt.NDArray[np.float32]]
    """Location of points. Should have shape (N, 3). Synchronized automatically when assigned."""
    colors: npt.NDArray[np.uint8]
    """Colors of points. Should have shape (N, 3) or (3,). Synchronized automatically when assigned."""
    point_size: float
    """Size of each point. Synchronized automatically when assigned."""
    point_shape: Literal["square", "diamond", "circle", "rounded", "sparkle"]
    """Shape to draw each point. Synchronized automatically when assigned."""
    precision: Literal["float16", "float32"]
    """Precision of the point cloud. Assignments to `points` are automatically casted
    based on the current precision value. Updates to `points` should therefore happen
    *after* updates to `precision`. Synchronized automatically when assigned."""

    def __post_init__(self):
        # Check shapes.
        assert len(self.points.shape) == 2
        assert self.colors.shape in ((3,), (self.points.shape[0], 3))
        assert self.points.shape[-1] == 3

        # Check dtypes.
        if self.precision == "float16":
            assert self.points.dtype == np.float16
        else:
            assert self.points.dtype == np.float32
        assert self.colors.dtype == np.uint8


@dataclasses.dataclass
class DirectionalLightMessage(_CreateSceneNodeMessage):
    """Directional light message."""

    props: DirectionalLightProps


@dataclasses.dataclass
class DirectionalLightProps:
    color: Tuple[int, int, int]
    """Color of the directional light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the directional light. Synchronized automatically when assigned."""
    cast_shadow: bool
    """If set to true mesh will cast a shadow. Synchronized automatically when assigned."""


@dataclasses.dataclass
class AmbientLightMessage(_CreateSceneNodeMessage):
    """Ambient light message."""

    props: AmbientLightProps


@dataclasses.dataclass
class AmbientLightProps:
    color: Tuple[int, int, int]
    """Color of the ambient light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the ambient light. Synchronized automatically when assigned."""


@dataclasses.dataclass
class HemisphereLightMessage(_CreateSceneNodeMessage):
    """Hemisphere light message."""

    props: HemisphereLightProps


@dataclasses.dataclass
class HemisphereLightProps:
    sky_color: Tuple[int, int, int]
    """Sky color of the hemisphere light. Synchronized automatically when assigned."""
    ground_color: Tuple[int, int, int]
    """Ground color of the hemisphere light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the hemisphere light. Synchronized automatically when assigned."""


@dataclasses.dataclass
class PointLightMessage(_CreateSceneNodeMessage):
    """Point light message."""

    props: PointLightProps


@dataclasses.dataclass
class PointLightProps:
    color: Tuple[int, int, int]
    """Color of the point light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the point light. Synchronized automatically when assigned."""
    distance: float
    """Distance of the point light. Synchronized automatically when assigned."""
    decay: float
    """Decay of the point light. Synchronized automatically when assigned."""
    cast_shadow: bool
    """If set to true mesh will cast a shadow. Synchronized automatically when assigned."""


@dataclasses.dataclass
class RectAreaLightMessage(_CreateSceneNodeMessage):
    """Rectangular Area light message."""

    props: RectAreaLightProps


@dataclasses.dataclass
class RectAreaLightProps:
    color: Tuple[int, int, int]
    """Color of the rectangular area light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the rectangular area light. Synchronized automatically when assigned."""
    width: float
    """Width of the rectangular area light. Synchronized automatically when assigned."""
    height: float
    """Height of the rectangular area light. Synchronized automatically when assigned."""


@dataclasses.dataclass
class SpotLightMessage(_CreateSceneNodeMessage):
    """Spot light message."""

    props: SpotLightProps


@dataclasses.dataclass
class SpotLightProps:
    color: Tuple[int, int, int]
    """Color of the spot light. Synchronized automatically when assigned."""
    intensity: float
    """Intensity of the spot light. Synchronized automatically when assigned."""
    distance: float
    """Distance of the spot light. Synchronized automatically when assigned."""
    angle: float
    """Angle of the spot light. Synchronized automatically when assigned."""
    penumbra: float
    """Penumbra of the spot light. Synchronized automatically when assigned."""
    decay: float
    """Decay of the spot light. Synchronized automatically when assigned."""
    cast_shadow: bool
    """If set to true mesh will cast a shadow. Synchronized automatically when assigned."""

    def __post_init__(self):
        assert self.angle <= np.pi / 2
        assert self.angle >= 0


@dataclasses.dataclass
class EnvironmentMapMessage(Message):
    """Environment Map message."""

    hdri: Union[
        Literal[
            "apartment",
            "city",
            "dawn",
            "forest",
            "lobby",
            "night",
            "park",
            "studio",
            "sunset",
            "warehouse",
        ],
        None,
    ]
    background: bool
    background_blurriness: float
    background_intensity: float
    background_wxyz: Tuple[float, float, float, float]
    environment_intensity: float
    environment_wxyz: Tuple[float, float, float, float]


@dataclasses.dataclass
class EnableLightsMessage(Message):
    """Default light message."""

    enabled: bool
    cast_shadow: bool


@dataclasses.dataclass
class MeshMessage(_CreateSceneNodeMessage):
    """Mesh message.

    Vertices are internally canonicalized to float32, faces to uint32."""

    props: MeshProps


@dataclasses.dataclass
class BoxMessage(_CreateSceneNodeMessage):
    """Box message."""

    props: BoxProps


@dataclasses.dataclass
class IcosphereMessage(_CreateSceneNodeMessage):
    """Icosphere message."""

    props: IcosphereProps


@dataclasses.dataclass
class MeshProps:
    vertices: npt.NDArray[np.float32]
    """A numpy array of vertex positions. Should have shape (V, 3). Synchronized automatically when assigned."""
    faces: npt.NDArray[np.uint32]
    """A numpy array of faces, where each face is represented by indices of vertices. Should have shape (F, 3). Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the mesh as RGB integers. Synchronized automatically when assigned."""
    wireframe: bool
    """Boolean indicating if the mesh should be rendered as a wireframe. Synchronized automatically when assigned."""
    opacity: Optional[float]
    """Opacity of the mesh. None means opaque. Synchronized automatically when assigned."""
    flat_shading: bool
    """Whether to do flat shading. Synchronized automatically when assigned."""
    side: Literal["front", "back", "double"]
    """Side of the surface to render. Synchronized automatically when assigned."""
    material: Literal["standard", "toon3", "toon5"]
    """Material type of the mesh. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""

    def __post_init__(self):
        # Check shapes.
        assert self.vertices.shape[-1] == 3
        assert self.faces.shape[-1] == 3


@dataclasses.dataclass
class BoxProps:
    dimensions: Tuple[float, float, float]
    """Dimensions of the box (x, y, z). Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the box as RGB integers. Synchronized automatically when assigned."""
    wireframe: bool
    """Boolean indicating if the box should be rendered as a wireframe. Synchronized automatically when assigned."""
    opacity: Optional[float]
    """Opacity of the box. None means opaque. Synchronized automatically when assigned."""
    flat_shading: bool
    """Whether to do flat shading. Synchronized automatically when assigned."""
    side: Literal["front", "back", "double"]
    """Side of the surface to render. Synchronized automatically when assigned."""
    material: Literal["standard", "toon3", "toon5"]
    """Material type of the box. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""


@dataclasses.dataclass
class IcosphereProps:
    radius: float
    """Radius of the icosphere. Synchronized automatically when assigned."""
    subdivisions: int
    """Number of subdivisions to use when creating the icosphere. Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the icosphere as RGB integers. Synchronized automatically when assigned."""
    wireframe: bool
    """Boolean indicating if the icosphere should be rendered as a wireframe. Synchronized automatically when assigned."""
    opacity: Optional[float]
    """Opacity of the icosphere. None means opaque. Synchronized automatically when assigned."""
    flat_shading: bool
    """Whether to do flat shading. Synchronized automatically when assigned."""
    side: Literal["front", "back", "double"]
    """Side of the surface to render. Synchronized automatically when assigned."""
    material: Literal["standard", "toon3", "toon5"]
    """Material type of the icosphere. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""


@dataclasses.dataclass
class SkinnedMeshMessage(_CreateSceneNodeMessage):
    """Skinned mesh message."""

    props: SkinnedMeshProps


@dataclasses.dataclass
class SkinnedMeshProps(MeshProps):
    """Mesh message.

    Vertices are internally canonicalized to float32, faces to uint32."""

    bone_wxyzs: npt.NDArray[np.float32]
    """Array of quaternions representing bone orientations (B, 4). Synchronized automatically when assigned."""
    bone_positions: npt.NDArray[np.float32]
    """Array of positions representing bone positions (B, 3). Synchronized automatically when assigned."""
    skin_indices: npt.NDArray[np.uint16]
    """Array of skin indices. Should have shape (V, 4). Synchronized automatically when assigned."""
    skin_weights: npt.NDArray[np.float32]
    """Array of skin weights. Should have shape (V, 4). Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""

    def __post_init__(self):
        # Check shapes.
        assert self.bone_wxyzs.shape[-1] == 4
        assert self.bone_positions.shape[-1] == 3
        assert self.bone_wxyzs.shape[0] == self.bone_positions.shape[0]
        assert self.vertices.shape[-1] == 3
        assert self.faces.shape[-1] == 3
        assert self.skin_weights is not None
        assert (
            self.skin_indices.shape
            == self.skin_weights.shape
            == (self.vertices.shape[0], 4)
        )


@dataclasses.dataclass
class BatchedMeshesMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying batched meshes information."""

    props: BatchedMeshesProps


@dataclasses.dataclass
class _BatchedMeshExtraProps:
    batched_wxyzs: npt.NDArray[np.float32]
    """Float array of shape (N, 4) representing quaternion rotations. Synchronized automatically when assigned."""
    batched_positions: npt.NDArray[np.float32]
    """Float array of shape (N, 3) representing positions. Synchronized automatically when assigned."""
    batched_scales: Optional[npt.NDArray[np.float32]]
    """Float array of shape (N,) or (N,3) representing uniform or per-axis (XYZ) scales. Synchronized automatically when assigned."""
    lod: Union[Literal["auto", "off"], Tuple[Tuple[float, float], ...]]
    """LOD settings. Either "auto", "off", or a tuple of (distance, ratio) pairs. Synchronized automatically when assigned."""

    def __post_init__(self):
        # Check shapes.
        assert self.batched_wxyzs.shape[-1] == 4
        assert self.batched_positions.shape[-1] == 3
        assert self.batched_wxyzs.shape[0] == self.batched_positions.shape[0]
        if self.batched_scales is not None:
            assert self.batched_scales.shape in (
                (self.batched_wxyzs.shape[0],),
                (self.batched_wxyzs.shape[0], 3),
            )


@dataclasses.dataclass
class BatchedMeshesProps(MeshProps, _BatchedMeshExtraProps):
    """Batched meshes message."""


@dataclasses.dataclass
class BatchedGlbMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying batched GLB information."""

    props: BatchedGlbProps


@dataclasses.dataclass
class BatchedGlbProps(GlbProps, _BatchedMeshExtraProps):
    """Batched GLB message."""


@dataclasses.dataclass
class SetBoneOrientationMessage(Message):
    """Server -> client message to set a skinned mesh bone's orientation.

    As with all other messages, transforms take the `T_parent_local` convention."""

    name: str
    bone_index: int
    wxyz: Tuple[float, float, float, float]

    @override
    def redundancy_key(self) -> str:
        return type(self).__name__ + "-" + self.name + "-" + str(self.bone_index)


@dataclasses.dataclass
class SetBonePositionMessage(Message):
    """Server -> client message to set a skinned mesh bone's position.

    As with all other messages, transforms take the `T_parent_local` convention."""

    name: str
    bone_index: int
    position: Tuple[float, float, float]

    @override
    def redundancy_key(self) -> str:
        return type(self).__name__ + "-" + self.name + "-" + str(self.bone_index)


@dataclasses.dataclass
class TransformControlsMessage(_CreateSceneNodeMessage):
    """Message for transform gizmos."""

    props: TransformControlsProps


@dataclasses.dataclass
class TransformControlsProps:
    scale: float
    """Scale of the transform controls. Synchronized automatically when assigned."""
    line_width: float
    """Width of the lines used in the gizmo. Synchronized automatically when assigned."""
    fixed: bool
    """Boolean indicating if the gizmo should be fixed in position. Synchronized automatically when assigned."""
    active_axes: Tuple[bool, bool, bool]
    """Tuple of booleans indicating active axes. Synchronized automatically when assigned."""
    disable_axes: bool
    """Tuple of booleans indicating if axes are disabled. These are used for
    translation in the X, Y, or Z directions. Synchronized automatically when
    assigned."""
    disable_sliders: bool
    """Tuple of booleans indicating if sliders are disabled. These are used for
    translation on the XY, YZ, or XZ planes. Synchronized automatically when
    assigned."""
    disable_rotations: bool
    """Tuple of booleans indicating if rotations are disabled. These are used
    for rotation around the X, Y, or Z axes. Synchronized automatically when
    assigned."""
    translation_limits: Tuple[
        Tuple[float, float], Tuple[float, float], Tuple[float, float]
    ]
    """Limits for translation. Synchronized automatically when assigned."""
    rotation_limits: Tuple[
        Tuple[float, float], Tuple[float, float], Tuple[float, float]
    ]
    """Limits for rotation. Synchronized automatically when assigned."""
    depth_test: bool
    """Boolean indicating if depth testing should be used when rendering.
    Setting to False can be used to render the gizmo even when occluded by
    other objects. Synchronized automatically when assigned."""
    opacity: float
    """Opacity of the gizmo. Synchronized automatically when assigned."""


@dataclasses.dataclass
class SetCameraPositionMessage(Message):
    """Server -> client message to set the camera's position."""

    position: Tuple[float, float, float]


@dataclasses.dataclass
class SetCameraUpDirectionMessage(Message):
    """Server -> client message to set the camera's up direction."""

    position: Tuple[float, float, float]


@dataclasses.dataclass
class SetCameraLookAtMessage(Message):
    """Server -> client message to set the camera's look-at point."""

    look_at: Tuple[float, float, float]


@dataclasses.dataclass
class SetCameraNearMessage(Message):
    """Server -> client message to set the camera's near clipping plane."""

    near: float


@dataclasses.dataclass
class SetCameraFarMessage(Message):
    """Server -> client message to set the camera's far clipping plane."""

    far: float


@dataclasses.dataclass
class SetCameraFovMessage(Message):
    """Server -> client message to set the camera's field of view."""

    fov: float


@dataclasses.dataclass
class SetOrientationMessage(Message):
    """Server -> client message to set a scene node's orientation.

    As with all other messages, transforms take the `T_parent_local` convention."""

    name: str
    wxyz: Tuple[float, float, float, float]


@dataclasses.dataclass
class SetPositionMessage(Message):
    """Server -> client message to set a scene node's position.

    As with all other messages, transforms take the `T_parent_local` convention."""

    name: str
    position: Tuple[float, float, float]


@dataclasses.dataclass
class TransformControlsUpdateMessage(Message):
    """Client -> server message when a transform control is updated.

    As with all other messages, transforms take the `T_parent_local` convention."""

    name: str
    wxyz: Tuple[float, float, float, float]
    position: Tuple[float, float, float]


@dataclasses.dataclass
class TransformControlsDragStartMessage(Message):
    """Client -> server message when a transform control drag starts."""

    name: str


@dataclasses.dataclass
class TransformControlsDragEndMessage(Message):
    """Client -> server message when a transform control drag ends."""

    name: str


@dataclasses.dataclass
class BackgroundImageMessage(Message):
    """Message for rendering a background image."""

    media_type: Literal["image/jpeg", "image/png"]
    rgb_data: Optional[bytes]
    depth_data: Optional[bytes]


@dataclasses.dataclass
class ImageMessage(_CreateSceneNodeMessage):
    """Message for rendering 2D images."""

    props: ImageProps


@dataclasses.dataclass
class ImageProps:
    media_type: Literal["image/jpeg", "image/png"]
    """Format of the provided image ('image/jpeg' or 'image/png'). Synchronized automatically when assigned."""
    _data: bytes
    """Binary data of the image. Synchronized automatically when assigned."""
    render_width: float
    """Width at which the image should be rendered in the scene. Synchronized automatically when assigned."""
    render_height: float
    """Height at which the image should be rendered in the scene. Synchronized automatically when assigned."""
    cast_shadow: bool
    """Whether or not to cast shadows. Synchronized automatically when assigned."""
    receive_shadow: bool
    """Whether or not to receive shadows. Synchronized automatically when assigned."""


@dataclasses.dataclass
class SetSceneNodeVisibilityMessage(Message):
    """Set the visibility of a particular node in the scene."""

    name: str
    visible: bool


@dataclasses.dataclass
class SetSceneNodeClickableMessage(Message):
    """Set the clickability of a particular node in the scene."""

    name: str
    clickable: bool


@dataclasses.dataclass
class SceneNodeClickMessage(Message):
    """Message for clicked objects."""

    name: str
    instance_index: Optional[int]
    """Instance index. Currently only used for batched axes."""
    ray_origin: Tuple[float, float, float]
    ray_direction: Tuple[float, float, float]
    screen_pos: Tuple[float, float]


@dataclasses.dataclass
class ResetGuiMessage(Message):
    """Reset GUI."""


@dataclasses.dataclass
class GuiBaseProps:
    """Base message type containing fields commonly used by GUI inputs."""

    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    label: str
    """Label text for the GUI element. Synchronized automatically when assigned."""
    hint: Optional[str]
    """Optional hint text for the GUI element. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the GUI element. Synchronized automatically when assigned."""
    disabled: bool
    """Disabled state of the GUI element. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiFolderProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    label: str
    """Label text for the GUI folder. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the GUI folder. Synchronized automatically when assigned."""
    expand_by_default: bool
    """Whether the folder should be expanded by default. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiFolderMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiFolderProps


@dataclasses.dataclass
class GuiMarkdownProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    _markdown: str
    """(Private) Markdown content to be displayed. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the markdown element. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiMarkdownMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiMarkdownProps


@dataclasses.dataclass
class GuiHtmlProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    content: str
    """HTML content to be displayed. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the markdown element. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiHtmlMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiHtmlProps


@dataclasses.dataclass
class GuiProgressBarProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    animated: bool
    """Whether the progress bar should be animated. Synchronized automatically when assigned."""
    color: Union[LiteralColor, Tuple[int, int, int], None]
    """Color of the progress bar. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the progress bar. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiProgressBarMessage(_CreateGuiComponentMessage):
    value: float
    container_uuid: str
    props: GuiProgressBarProps


@dataclasses.dataclass
class GuiPlotlyProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    _plotly_json_str: str
    """(Private) JSON string representation of the Plotly figure. Synchronized automatically when assigned."""
    aspect: float
    """Aspect ratio of the plot. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the plot. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiPlotlyMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiPlotlyProps


@dataclasses.dataclass
class GuiUplotProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    data: Tuple[npt.NDArray[np.float64], ...]
    """Tuple of 1D numpy arrays containing chart data. First array is x-axis data,
    subsequent arrays are y-axis data for each series. All arrays must have matching
    lengths. Minimum 2 arrays required. Synchronized automatically when assigned."""
    mode: Union[Literal[1, 2], None]
    """Chart layout mode: 1 = aligned (all series share axes), 2 = faceted (each series
    gets its own subplot panel). Defaults to 1. Synchronized automatically when assigned."""
    title: Union[str, None]
    """Chart title displayed at the top of the plot. Synchronized automatically when assigned."""
    series: Tuple[uplot.Series, ...]
    """Series configuration objects defining visual appearance (colors, line styles, labels)
    and behavior for each data array. Must match data tuple length. Synchronized automatically when assigned."""
    bands: Union[Tuple[uplot.Band, ...], None]
    """High/low range visualizations between adjacent series indices. Useful for confidence
    intervals, error bounds, or min/max ranges. Synchronized automatically when assigned."""
    scales: Union[Dict[str, uplot.Scale], None]
    """Scale definitions controlling data-to-pixel mapping and axis ranges. Enables features
    like auto-ranging, manual bounds, time-based scaling, and logarithmic distributions.
    Multiple scales support dual-axis charts. Synchronized automatically when assigned."""
    axes: Union[Tuple[uplot.Axis, ...], None]
    """Axis configuration for positioning (top/right/bottom/left), tick formatting, grid
    styling, and spacing. Controls visual appearance of chart axes. Synchronized automatically when assigned."""
    legend: Union[uplot.Legend, None]
    """Legend display options including positioning, styling, and custom value formatting
    for hover states. Synchronized automatically when assigned."""
    cursor: Union[uplot.Cursor, None]
    """Interactive cursor behavior including hover detection, drag-to-zoom, and crosshair
    appearance. Controls user interaction with the chart. Synchronized automatically when assigned."""
    focus: Union[uplot.Focus, None]
    """Visual highlighting when hovering over series. Controls alpha transparency of
    non-focused series to emphasize the active one. Synchronized automatically when assigned."""
    aspect: float
    """Width-to-height ratio for chart display (width/height). 1.0 = square, >1.0 = wider.
    Synchronized automatically when assigned."""
    visible: bool
    """Whether the chart is visible in the interface. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiUplotMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiUplotProps


@dataclasses.dataclass
class GuiImageProps:
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    label: Optional[str]
    """Label text for the image. Synchronized automatically when assigned."""
    _data: Optional[bytes]
    """Binary data of the image. Synchronized automatically when assigned."""
    media_type: Literal["image/jpeg", "image/png"]
    """Format of the provided image ('image/jpeg' or 'image/png'). Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the image. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiImageMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiImageProps


@dataclasses.dataclass
class GuiTabGroupProps:
    _tab_labels: Tuple[str, ...]
    """(Private) Tuple of labels for each tab. Synchronized automatically when assigned."""
    _tab_icons_html: Tuple[Union[str, None], ...]
    """(Private) Tuple of HTML strings for icons of each tab, or None if no icon. Synchronized automatically when assigned."""
    _tab_container_ids: Tuple[str, ...]
    """(Private) Tuple of container IDs for each tab. Synchronized automatically when assigned."""
    order: float
    """Order value for arranging GUI elements. Synchronized automatically when assigned."""
    visible: bool
    """Visibility state of the tab group. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiTabGroupMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiTabGroupProps


@dataclasses.dataclass
class GuiModalMessage(Message):
    order: float
    uuid: str
    title: str

    @override
    def redundancy_key(self) -> str:
        return f"modal-{self.uuid}"


@dataclasses.dataclass
class GuiCloseModalMessage(Message):
    uuid: str

    @override
    def redundancy_key(self) -> str:
        return f"modal-{self.uuid}"


@dataclasses.dataclass
class GuiButtonProps(GuiBaseProps):
    color: Union[LiteralColor, Tuple[int, int, int], None]
    """Color of the button. Synchronized automatically when assigned."""
    _icon_html: Optional[str]
    """(Private) HTML string for the icon to be displayed on the button. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiButtonMessage(_CreateGuiComponentMessage):
    value: bool
    container_uuid: str
    props: GuiButtonProps


@dataclasses.dataclass
class GuiUploadButtonProps(GuiBaseProps):
    color: Union[LiteralColor, Tuple[int, int, int], None]
    """Color of the upload button. Synchronized automatically when assigned."""
    _icon_html: Optional[str]
    """(Private) HTML string for the icon to be displayed on the upload button. Synchronized automatically when assigned."""
    mime_type: str
    """MIME type of the files that can be uploaded. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiUploadButtonMessage(_CreateGuiComponentMessage):
    container_uuid: str
    props: GuiUploadButtonProps


@dataclasses.dataclass
class GuiSliderProps(GuiBaseProps):
    min: float
    """Minimum value for the slider. Synchronized automatically when assigned."""
    max: float
    """Maximum value for the slider. Synchronized automatically when assigned."""
    step: float
    """Step size for the slider. Synchronized automatically when assigned."""
    precision: int
    """Number of decimal places to display for the slider value. Synchronized automatically when assigned."""
    _marks: Optional[Tuple[GuiSliderMark, ...]]
    """(Private) Optional tuple of GuiSliderMark objects to display custom marks on the slider. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiSliderMessage(_CreateGuiComponentMessage):
    value: float
    container_uuid: str
    props: GuiSliderProps


@dataclasses.dataclass
class GuiMultiSliderProps(GuiBaseProps):
    min: float
    """Minimum value for the multi-slider. Synchronized automatically when assigned."""
    max: float
    """Maximum value for the multi-slider. Synchronized automatically when assigned."""
    step: float
    """Step size for the multi-slider. Synchronized automatically when assigned."""
    min_range: Optional[float]
    """Minimum allowed range between slider handles. Synchronized automatically when assigned."""
    precision: int
    """Number of decimal places to display for the multi-slider values. Synchronized automatically when assigned."""
    fixed_endpoints: bool
    """If True, the first and last handles cannot be moved. Synchronized automatically when assigned."""
    _marks: Optional[Tuple[GuiSliderMark, ...]]
    """(Private) Optional tuple of GuiSliderMark objects to display custom marks on the multi-slider. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiMultiSliderMessage(_CreateGuiComponentMessage):
    value: Tuple[float, ...]
    container_uuid: str
    props: GuiMultiSliderProps


@dataclasses.dataclass
class GuiNumberProps(GuiBaseProps):
    precision: int
    """Number of decimal places to display for the number value. Synchronized automatically when assigned."""
    step: float
    """Step size for incrementing/decrementing the number value. Synchronized automatically when assigned."""
    min: Optional[float]
    """Minimum allowed value for the number input. Synchronized automatically when assigned."""
    max: Optional[float]
    """Maximum allowed value for the number input. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiNumberMessage(_CreateGuiComponentMessage):
    value: float
    container_uuid: str
    props: GuiNumberProps


@dataclasses.dataclass
class GuiRgbProps(GuiBaseProps):
    pass


@dataclasses.dataclass
class GuiRgbMessage(_CreateGuiComponentMessage):
    value: Tuple[int, int, int]
    container_uuid: str
    props: GuiRgbProps


@dataclasses.dataclass
class GuiRgbaProps(GuiBaseProps):
    pass


@dataclasses.dataclass
class GuiRgbaMessage(_CreateGuiComponentMessage):
    value: Tuple[int, int, int, int]
    container_uuid: str
    props: GuiRgbaProps


@dataclasses.dataclass
class GuiCheckboxProps(GuiBaseProps):
    pass


@dataclasses.dataclass
class GuiCheckboxMessage(_CreateGuiComponentMessage):
    value: bool
    container_uuid: str
    props: GuiCheckboxProps


@dataclasses.dataclass
class GuiVector2Props(GuiBaseProps):
    min: Optional[Tuple[float, float]]
    """Minimum allowed values for each component of the vector. Synchronized automatically when assigned."""
    max: Optional[Tuple[float, float]]
    """Maximum allowed values for each component of the vector. Synchronized automatically when assigned."""
    step: float
    """Step size for incrementing/decrementing each component of the vector. Synchronized automatically when assigned."""
    precision: int
    """Number of decimal places to display for each component of the vector. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiVector2Message(_CreateGuiComponentMessage):
    value: Tuple[float, float]
    container_uuid: str
    props: GuiVector2Props


@dataclasses.dataclass
class GuiVector3Props(GuiBaseProps):
    min: Optional[Tuple[float, float, float]]
    """Minimum allowed values for each component of the vector. Synchronized automatically when assigned."""
    max: Optional[Tuple[float, float, float]]
    """Maximum allowed values for each component of the vector. Synchronized automatically when assigned."""
    step: float
    """Step size for incrementing/decrementing each component of the vector. Synchronized automatically when assigned."""
    precision: int
    """Number of decimal places to display for each component of the vector. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiVector3Message(_CreateGuiComponentMessage):
    value: Tuple[float, float, float]
    container_uuid: str
    props: GuiVector3Props


@dataclasses.dataclass
class GuiTextProps(GuiBaseProps):
    multiline: bool


@dataclasses.dataclass
class GuiTextMessage(_CreateGuiComponentMessage):
    value: str
    container_uuid: str
    props: GuiTextProps


@dataclasses.dataclass
class GuiDropdownProps(GuiBaseProps):
    # This will actually be manually overridden for better types.
    options: Tuple[str, ...]
    """Tuple of options for the dropdown. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiDropdownMessage(_CreateGuiComponentMessage):
    value: str
    container_uuid: str
    props: GuiDropdownProps


@dataclasses.dataclass
class GuiButtonGroupProps(GuiBaseProps):
    options: Tuple[str, ...]
    """Tuple of buttons for the button group. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GuiButtonGroupMessage(_CreateGuiComponentMessage):
    value: str
    container_uuid: str
    props: GuiButtonGroupProps


@dataclasses.dataclass
class GuiUpdateMessage(Message):
    """Sent client<->server when any property of a GUI component is changed."""

    uuid: str
    updates: Dict[str, Any]
    """Mapping from property name to new value."""

    @override
    def redundancy_key(self) -> str:
        return (
            type(self).__name__
            + "-"
            + self.uuid
            + "-"
            + ",".join(list(self.updates.keys()))
        )


@dataclasses.dataclass
class SceneNodeUpdateMessage(Message):
    """Sent client<->server when any property of a scene node is changed."""

    name: str
    updates: Dict[str, Any]
    """Mapping from property name to new value."""

    @override
    def redundancy_key(self) -> str:
        return (
            type(self).__name__
            + "-"
            + self.name
            + "-"
            + ",".join(list(self.updates.keys()))
        )


@dataclasses.dataclass
class ThemeConfigurationMessage(Message):
    """Message from server->client to configure parts of the GUI."""

    titlebar_content: Optional[theme.TitlebarConfig]
    control_layout: Literal["floating", "collapsible", "fixed"]
    control_width: Literal["small", "medium", "large"]
    show_logo: bool
    show_share_button: bool
    dark_mode: bool
    colors: Optional[Tuple[str, str, str, str, str, str, str, str, str, str]]


@dataclasses.dataclass
class LineSegmentsMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying line segments information."""

    props: LineSegmentsProps


@dataclasses.dataclass
class LineSegmentsProps:
    points: npt.NDArray[np.float32]
    """A numpy array of shape (N, 2, 3) containing a batched set of line
    segments. Synchronized automatically when assigned."""
    line_width: float
    """Width of the lines. Synchronized automatically when assigned."""
    colors: npt.NDArray[np.uint8]
    """Numpy array of shape (N, 2, 3) containing a color for each point.
    Synchronized automatically when assigned."""


@dataclasses.dataclass
class CatmullRomSplineMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying Catmull-Rom spline information."""

    props: CatmullRomSplineProps


@dataclasses.dataclass
class CatmullRomSplineProps:
    points: npt.NDArray[np.float32]
    """Array with shape (N, 3) defining the spline's path. Synchronized
    automatically when assigned."""
    curve_type: Literal["centripetal", "chordal", "catmullrom"]
    """Type of the curve ('centripetal', 'chordal', 'catmullrom'). Synchronized automatically when assigned."""
    tension: float
    """Tension of the curve. Affects the tightness of the curve. Synchronized automatically when assigned."""
    closed: bool
    """Boolean indicating if the spline is closed (forms a loop). Synchronized automatically when assigned."""
    line_width: float
    """Width of the spline line. Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the spline as RGB integers. Synchronized automatically when assigned."""
    segments: Optional[int]
    """Number of segments to divide the spline into. Synchronized automatically when assigned."""


@dataclasses.dataclass
class CubicBezierSplineMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying Cubic Bezier spline information."""

    props: CubicBezierSplineProps


@dataclasses.dataclass
class CubicBezierSplineProps:
    points: npt.NDArray[np.float32]
    """Array of shape (N, 3) defining the spline's key points. Synchronized
    automatically when assigned."""
    control_points: npt.NDArray[np.float32]
    """Array of shape (2*N-2, 3) defining control points for Bezier curve shaping. Synchronized automatically when assigned."""
    line_width: float
    """Width of the spline line. Synchronized automatically when assigned."""
    color: Tuple[int, int, int]
    """Color of the spline as RGB integers. Synchronized automatically when assigned."""
    segments: Optional[int]
    """Number of segments to divide the spline into. Synchronized automatically when assigned."""


@dataclasses.dataclass
class GaussianSplatsMessage(_CreateSceneNodeMessage):
    """Message from server->client carrying splattable Gaussians."""

    props: GaussianSplatsProps


@dataclasses.dataclass
class GaussianSplatsProps:
    # Memory layout is borrowed from:
    # https://github.com/antimatter15/splat
    buffer: npt.NDArray[np.uint32]
    """Our buffer will contain:
    - x as f32
    - y as f32
    - z as f32
    - (unused)
    - cov1 (f16), cov2 (f16)
    - cov3 (f16), cov4 (f16)
    - cov5 (f16), cov6 (f16)
    - rgba (int32)

    Where cov1-6 are the upper-triangular terms of covariance matrices."""


@dataclasses.dataclass
class GetRenderRequestMessage(Message):
    """Message from server->client requesting a render from a specified camera
    pose."""

    format: Literal["image/jpeg", "image/png"]
    height: int
    width: int
    quality: int

    wxyz: Tuple[float, float, float, float]
    position: Tuple[float, float, float]
    fov: float


@dataclasses.dataclass
class GetRenderResponseMessage(Message):
    """Message from client->server carrying a render."""

    payload: bytes


@dataclasses.dataclass
class FileTransferStartUpload(Message):
    """Signal that a file is about to be sent.

    This message is used to upload files from clients to the server.
    """

    source_component_uuid: str
    transfer_uuid: str
    filename: str
    mime_type: str
    part_count: int
    size_bytes: int

    @override
    def redundancy_key(self) -> str:
        return type(self).__name__ + "-" + self.transfer_uuid


@dataclasses.dataclass
class FileTransferStartDownload(Message):
    """Signal that a file is about to be sent.

    This message is used to send files to clients from the server.
    """

    save_immediately: bool
    transfer_uuid: str
    filename: str
    mime_type: str
    part_count: int
    size_bytes: int

    @override
    def redundancy_key(self) -> str:
        return type(self).__name__ + "-" + self.transfer_uuid


@dataclasses.dataclass
class FileTransferPart(Message):
    """Send a file for clients to download or upload files from client."""

    source_component_uuid: Optional[str]
    transfer_uuid: str
    part_index: int
    content: bytes

    @override
    def redundancy_key(self) -> str:
        return (
            type(self).__name__ + "-" + self.transfer_uuid + "-" + str(self.part_index)
        )


@dataclasses.dataclass
class FileTransferPartAck(Message):
    """Send a file for clients to download or upload files from client."""

    source_component_uuid: Optional[str]
    transfer_uuid: str
    transferred_bytes: int
    total_bytes: int

    @override
    def redundancy_key(self) -> str:
        return (
            type(self).__name__
            + "-"
            + self.transfer_uuid
            + "-"
            + str(self.transferred_bytes)
        )


@dataclasses.dataclass
class ShareUrlRequest(Message):
    """Message from client->server to connect to the share URL server."""


@dataclasses.dataclass
class ShareUrlUpdated(Message):
    """Message from server->client to indicate that the share URL has been updated."""

    share_url: Optional[str]


@dataclasses.dataclass
class ShareUrlDisconnect(Message):
    """Message from client->server to disconnect from the share URL server."""


@dataclasses.dataclass
class SetGuiPanelLabelMessage(Message):
    """Message from server->client to set the label of the GUI panel."""

    label: Optional[str]
