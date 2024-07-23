"""
Write each run to a NeXus/HDF5 file.

IMPORTANT
See the note about waiting for the nxwriter to finish AFTER EACH ACQUISITION!
https://bcda-aps.github.io/apstools/dev/api/_filewriters.html#apstools.callbacks.nexus_writer.NXWriter
"""

__all__ = ["nxwriter"]

import logging

from apstools.callbacks import NXWriterAPS

# from .. import iconfig
from ..utils.iconfig_loader import iconfig

logger = logging.getLogger(__name__)
logger.info(__file__)

XPCS_LAYOUT_VERSION = "APS-8IDI-202310"
NEXUS_RELEASE = "v2022.07"  # NeXus release to which this file is written


class MyNXWriter(NXWriterAPS):
    """
    Modify the default behavior of NXWriter for XPCS.
    """

    def write_root(self, filename):
        super().write_root(filename)
        self.root.attrs["NeXus_version"] = NEXUS_RELEASE
        self.root.attrs["xpcs_layout_version"] = XPCS_LAYOUT_VERSION

    def write_entry(self):
        nxentry = super().write_entry()
        ds = nxentry.create_dataset("xpcs_layout_version", data=XPCS_LAYOUT_VERSION)
        ds.attrs["target"] = ds.name
        nxentry["instrument/layout_version"] = ds

        nxentry["entry_identifier_uuid"] = nxentry["entry_identifier"]
        # scan_number is deprecated, see NXxpcs docs (linking content anyway)
        nxentry["scan_number"] = nxentry["entry_identifier"]

        # data:NXdata (optional, with NeXus v2022.07)
        # NOTE:NXnote (optional, replace "NOTE" as appropriate)

    def write_instrument(self, parent):
        super().write_instrument(parent)
        nxinstrument = parent["instrument"]
        self.write_attenuator(nxinstrument, "attenuator")

        nxbeam = self.write_beam(nxinstrument, "incident_beam")
        mdgroup = nxinstrument["bluesky/metadata"]

        ds = mdgroup["X_energy"]
        ds.attrs["units"] = "keV"
        nxbeam["incident_energy"] = ds

        ds = mdgroup["incident_beam_size_nm_xy"]
        ds.attrs["units"] = "nm"
        nxbeam["extent"] = ds  # 2D size of incident beam

        for k in "I0 I1 incident_energy_spread".split():
            nxbeam[k] = mdgroup[k]

        self.write_beam(nxinstrument, "BPM")

        # masks:NXnote (optional, not appropriate for raw data file)

    def write_attenuator(self, parent, name="attenuator"):
        self.create_NX_group(parent, f"{name}:NXattenuator")

    def write_beam(self, parent, name="incident_beam"):
        nxbeam = self.create_NX_group(parent, f"{name}:NXbeam")
        return nxbeam

    def write_detector(self, parent):
        super().write_detector(parent)

        nxdet = self.create_NX_group(parent, "lambda2M:NXdetector")
        parent["detector_1"] = nxdet  # convenience link
        nxdet.create_dataset("description", data="lambda2M")  # not in metadata

        # links from bluesky/metadata fields
        # md created in user's plan:
        #   /home/8ididata/2023-2/pvaccess_test/bp_Nexus_Lambda2M.py
        #   gather_dm_metadata()
        # TODO: To coordinate with those names, that code should be
        #   located in the instrument package itself.
        mdgroup = parent["bluesky/metadata"]
        nxdet["beam_center_x"] = mdgroup["bcx"]
        nxdet["beam_center_y"] = mdgroup["bcy"]
        nxdet["distance"] = mdgroup["det_dist"]
        nxdet["x_pixel_size"] = mdgroup["pix_dim_x"]
        nxdet["y_pixel_size"] = mdgroup["pix_dim_y"]
        nxdet["count_time"] = mdgroup["t1"]  # AD's acquire_time
        nxdet["frame_time"] = mdgroup["t1"]  # AD's acquire_time
        nxdet["acquire_period"] = mdgroup["t0"]  # AD's acquire_period

    def write_sample(self, parent):
        nxsample = super().write_sample(parent)
        # nxsample = parent.get("sample")
        if nxsample is None:
            logger.debug("No '/entry/sample' group found.")
            return
        mdgroup = parent["instrument/bluesky/metadata"]

        for chan in range(1, 4):
            v = mdgroup.get(f"sample_temperature{chan}")
            if v is not None:
                nxsample[f"temperature{chan}"] = v
                nxsample[f"temperature{chan}"].attrs["units"] = "C"

        def write_positioner(name, md_name, units):
            """Per NXsample, use NXpositioner group for each."""
            v = mdgroup.get(name)
            if v is not None:
                group = self.create_NX_group(nxsample, f"{name}:NXpositioner")
                group["value"] = v
                group["value"].attrs["units"] = units

        write_positioner("x", "sample_x_mm", "mm")
        write_positioner("y", "sample_y_mm", "mm")
        write_positioner("z", "sample_z_mm", "mm")

        write_positioner("roll", "sample_roll_degrees", "degrees")
        write_positioner("pitch", "sample_pitch_degrees", "degrees")
        write_positioner("yaw", "sample_yaw_degrees", "degrees")

        nxbeam = self.write_beam(nxsample, "beam")
        v = mdgroup.get("sample_beam_intensity")
        if v is not None:
            nxbeam["intensity"] = v
        v = mdgroup.get("sample_beam_size_nm_xy")
        if v is not None:
            nxbeam["extent"].attrs["units"] = "nm"

    def get_sample_title(self):
        """
        Get the title from the metadata or modify the default.

        default title: S{scan_id}-{plan_name}-{short_uid}
        """
        try:
            title = f'S{self.scan_id:05d}-{self.metadata["title"]}'
        except KeyError:
            # title = super().get_sample_title()  # the default title
            title = f"S{self.scan_id:05d}-{self.plan_name}-{self.uid[:7]}"
        return title

    def write_stream_external(self, parent, d, subgroup, stream_name, k, v):
        """
        Modify the default behavior of NXWriter.  Don't copy the image.

        The design is to have all HDF5 files (metadata, image, analysis) in the
        same directory.  This makes it easy to create external file links.

        BUT, some detectors do not create an HDF5 file. We'll have to re-visit
        external links when we get such a detector.

        Do not delay by waiting for the image file to close, then copying the
        image data to the one NeXus file.

        Advice is to ALWAYS use a RELATIVE file path with ExternalLink.  When
        the master:external file pair are moved, the new location can construct
        the expected relative path using softlinks (or Windows aliases).
        """
        resource_id = self.get_unique_resource(d)
        fname = self.getResourceFile(resource_id)

        # # Link to image file in the same directory.
        # h5addr = "/entry/data/data"  # NeXus default data address.
        # subgroup["value"] = h5py.ExternalLink(fname.name, h5addr)

        ds = subgroup.create_dataset("image_file_name", data=fname.name)
        ds.attrs["bluesky_resource_id"] = resource_id
        ds.attrs["shape"] = v.get("shape", "")
        ds.attrs["target"] = ds.name

    def get_ioc_file_path(self):
        import pathlib

        from ..devices.ad_lambda2M import LAMBDA2M_FILES_ROOT

        # NOTE: The default is specific for the Lambda2M detector!
        # Actual IOC file path is not present in the resource or datum docs.
        # Get from run's metadata or pick default.

        dir = self.metadata.get("ADIOC_FILE_DIR", LAMBDA2M_FILES_ROOT)
        return pathlib.Path(dir)

    def get_unique_resource(self, datum_id_list):
        # count number of unique resources (expect only 1)
        resource_id_list = []
        for datum_id in datum_id_list:
            resource_id = self.externals[datum_id]["resource"]
            if resource_id not in resource_id_list:
                resource_id_list.append(resource_id)
        if len(resource_id_list) != 1:
            # fmt: off
            raise ValueError(
                f"{len(resource_id_list)}"
                f" unique resource UIDs: {resource_id_list}"
            )
            # fmt: on
        return resource_id_list[0]


nxwriter = MyNXWriter()  # create the callback instance
# RE.subscribe(nxwriter.receiver)  # subscribe to the RunEngine

warn_missing = iconfig.get("NEXUS_WARN_MISSING_CONTENT", False)
nxwriter.warn_on_missing_content = warn_missing
nxwriter.file_extension = iconfig.get("NEXUS_FILE_EXTENSION", "hdf")

# NeXus files are written into current working directory.  Here are the controls:
# nxwriter.file_path = pathlib.Path("XPCS may want to override!!!")
# nxwriter.file_name = pathlib.Path("XPCS may want to override!!!")
# https://github.com/BCDA-APS/apstools/blob/main/apstools/callbacks/nexus_writer.py#L297
