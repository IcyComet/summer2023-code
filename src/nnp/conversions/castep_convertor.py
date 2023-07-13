
import numpy as np
import ase
from ase.calculators.singlepoint import SinglePointCalculator
import re

from .general_convertor import General_Convertor
   
#TODO review the class hierarchy for possible restructuring
class Castep_Convertor(General_Convertor):
    """General class to be inherited by readers of Castep output files.
    Parameters: 
        file: file objected opened for reading
    NOTE set errors="replace" when opening files or catch UnicodeDecodeErrors.
    UnicodeDecodeError checks need to happen before ValueError if they are handled differently.
    """

    def __init__(self, file):
        super(Castep_Convertor, self).__init__(file)

        self.file.seek(0)

        #  find the end of the fiel
        self.file_size = self.file.seek(0,2)
        self.file.seek(0)
        return
    
    class NextMDIterationError(Exception):
        """Unexpectedly encountered the start of the next MD iteration"""
    
    def read_cell(self):
        """Reads the unit cell from the file.
        """
        while (line := self.file.readline()) and (re.fullmatch("Unit Cell", line.strip()) is None):
            pass
        
        self.move(2)
        mat = self.read_matrix()
        cell = mat[:, :3]
        return cell
    
    def move(self, n: int):
        """Moves the file pointer n lines forward.
        """
        for _ in range(n):
            self.file.readline()
    
    def read_positions(self):
        """Reads the positions from the file.
        """
        
        # find the positions
        while (line := self.file.readline()) and (re.search("Fractional coordinates of atoms", line) is None):
            pass
        self.move(2)

        positions = []
        symbols = []

        while (line := self.file.readline()) and (re.fullmatch("x+", line.strip()) is None):
            words = line.split()
            symbols.append(words[1])
            positions.append([float(x) for x in words[3:6]])
        
        return positions, symbols
    
    def read_forces(self):
        """Reads the forces from the file.
        """

        # find the forces
        while (line := self.file.readline()) and \
            (re.fullmatch("\*+ Forces \*+", line.strip()) is None):

            if re.search("Starting MD iteration", line) is not None:
                raise self.NextMDIterationError()
        
        self.move(5)
        
        forces = []
        
        while (line := self.file.readline()) and (re.fullmatch("\s*\*\s+\*\s*", line) is None):
            forces.append([float(x) for x in line.split()[3:6]])
        
        return forces
    
    def check_EOF(self):
        return self.file.tell() >= self.file_size
    
    def read_energy(self):
        raise NotImplementedError


class Castep_MD_Convertor(Castep_Convertor):
    """Class for reading of Castep MD output files.
    Parameters: 
        file: file objected opened for reading
    """

    def __init__(
            self, 
            file: str,
            finite_set_correction: bool = False):
        
        super(Castep_MD_Convertor, self).__init__(file)

    def read(self, pbc: bool = True) -> list:
        """Reads the file and returns a list of ase.Atoms objects.
        TODO decide the loop condition
        """
        traj = []
        cell = self.read_cell()

        while not self.check_EOF(): #TODO
            try:

                cell_positions, symbols = self.read_positions()

                positions = [cell.dot(np.array(pos)) for pos in cell_positions]

                forces = self.read_forces()

                energy = self.read_energy()

                atoms = ase.Atoms(symbols = symbols, positions=positions, cell=cell)
                atoms.calc = SinglePointCalculator(atoms=atoms, energy=energy, forces=forces)
                atoms.set_pbc((pbc, pbc, pbc))
                traj.append(atoms)
            
            # except UnicodeDecodeError: # Needs to be caught before ValueError
            #     break

            except (UnboundLocalError, IndexError, ValueError):
                
                while (line := self.file.readline()) and \
                    (re.search("Starting MD iteration", line) is None):
                    pass

                if not line: #TODO decide if necessary once loop condition is chosen
                    break
            
            except(self.NextMDIterationError):
                continue
          
        return traj

    def read_energy(self):
        """Reads the energy from the file.
        """

        pattern = re.compile("Potential Energy: (\-?\d+\.\d+)")
        while (line := self.file.readline()) and (x := pattern.search(line)) is None:
            
            if re.search("Starting MD iteration", line) is not None:
                raise self.NextMDIterationError()
        
        return float(x.group(1))
    
    
    def count_iterations(self) -> int:
        """Counts the number of completed MD iterations in the file.
        i+1 is the expected number of Atoms objects including initial configuration."""
        self.file.seek(0)
        pattern = re.compile("finished MD iteration\s+([0-9]+)") #
        i = 0
        while (line := self.file.readline()):
            if pattern.search(line) is not None:
                i += 1
        self.file.seek(0)
        return i


class Castep_SCF_Convertor(Castep_Convertor):
    """Class for reading of Castep scf output files.
    Parameters: 
        file: file objected opened for reading
    NOTE haven't used this class at all but modified behaviour of read_positions in superclass
    """
    
    def __init__(self, file: str, finite_set_correction: bool = False):
        super(Castep_SCF_Convertor, self).__init__(file)
        
        self.energy_mark = ['Final', 'energy,', 'E']
        self.energy_slice = slice(0, 3)

        if finite_set_correction:
            self.energy_mark = ['Total', 'energy', 'corrected', 'for', 'finite', 'basis', 'set']
            self.energy_slice = slice(-7, -0)
            
    
    def read(self, pbc: bool = True):
        """Reads the file and returns a list of ase.Atoms objects.        
        """

        # find the cell
        cell = self.read_cell()
        cell_positions, symbols = self.read_positions()

        # read the positions
        positions = [cell.dot(np.array(pos)) for pos in cell_positions]

        # read the energy and forces
        energy = self.read_energy()
        forces = self.read_forces()
        
        # create the atoms object
        atoms = ase.Atoms(symbols = symbols,
            positions=positions, cell=cell, pbc=pbc)
        
        atoms.calc = SinglePointCalculator(atoms=atoms, energy=energy, forces=forces)

        return [atoms]
        
    def read_energy(self):
        """Reads the energy from the file.
        """
        
        i = 0
        
        line = self.file.readline().split()
        cont = line[self.energy_slice] != self.energy_mark 

        # find the energy
        while cont and not self.check_EOF():
            line = self.file.readline().split()    
            i+=1
            cont = line[self.energy_slice] != self.energy_mark 

        energy = float(line[-2])
        return energy