from gpyumd.util import check_list, check_range
from numpy import prod

__author__ = "Alexander Gabourie"
__email__ = "agabourie47@gmail.com"


#########################################
# Structure preprocessing
#########################################

def set_velocities(atoms, custom=None):
    """
    Sets the 'velocity' part of the atoms to be used in GPUMD.
    Custom velocities must be provided. They must also be in
    the units of eV^(1/2) amu^(-1/2).

    Args:
        atoms (ase.Atoms):
            Atoms to assign velocities to.

        custom (list(list)):
             list of len(atoms) with each element made from
             a 3-element list for [vx, vy, vz]

    """
    if not custom:
        raise ValueError("No velocities provided.")

    num_atoms = len(atoms)
    info = atoms.info
    if not len(custom) == num_atoms:
        return ValueError('Incorrect number of velocities for number of atoms.')
    for index, (atom, velocity) in enumerate(zip(atoms, custom)):
        if not len(velocity) == 3:
            return ValueError('Three components of velocity not provided.')
        index = __init_index(index, info, num_atoms)
        info[index]['velocity'] = velocity
    __handle_end(info, num_atoms)
    atoms.info = info


def __init_index2(index, info): # TODO merge this with other __init_index function
    if index not in info.keys():
        info[index] = dict()


def add_basis(atoms, index=None, mapping=None):
    """
    Assigns a basis index for each atom in atoms. Updates atoms.

    Args:
        atoms (ase.Atoms):
            Atoms to assign basis to.

        index (list(int)):
            Atom indices of those in the unit cell. Order is important.

        mapping (list(int)):
            Mapping of all atoms to the relevant basis positions


    """
    n = atoms.get_global_number_of_atoms()
    info = atoms.info
    info['unitcell'] = list()
    if index:
        if (mapping is None) or (len(mapping) != n):
            raise ValueError("Full atom mapping required if index is provided.")
        for idx in index:
            info['unitcell'].append(idx)
        for idx in range(n):
            __init_index2(idx, info)
            info[idx]['basis'] = mapping[idx]
    else:
        for idx in range(n):
            info['unitcell'].append(idx)
            # if no index provided, assume atoms is unit cell
            __init_index2(idx, info)
            info[idx]['basis'] = idx


def repeat(atoms, rep):
    """
    A wrapper of ase.Atoms.repeat that is aware of GPUMD's basis information.

    Args:
        atoms (ase.Atoms):
            Atoms to assign velocities to.

        rep (int | list(3 ints)):
            List of three positive integers or a single integer

    """
    rep = check_list(rep, varname='rep', dtype=int)
    replen = len(rep)
    if replen == 1:
        rep = rep*3
    elif not replen == 3:
        raise ValueError("rep must be a sequence of 1 or 3 integers.")
    check_range(rep, 2 ** 64)
    supercell = atoms.repeat(rep)
    sinfo = supercell.info
    ainfo = atoms.info
    n = atoms.get_global_number_of_atoms()
    for i in range(1, prod(rep, dtype=int)):
        for j in range(n):
            sinfo[i*n+j] = {'basis': ainfo[j]['basis']}

    return supercell
