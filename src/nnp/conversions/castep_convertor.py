
import numpy as np
import ase
from ase.calculators.singlepoint import SinglePointCalculator
import re

from .general_convertor import General_Convertor
   

class Castep_Convertor(General_Convertor):
    """General class to be inherited by readers of Castep output files.
    Parameters: 
        file: file objected opened for reading
        max_iter (int): how long to keep looping through a file with unexpected outcome
            before ending the code.
    """

    def __init__(self, file):
        super(Castep_Convertor, self).__init__(file)

        self.file.seek(0)

        #  find the end of the fiel
        self.file_size = self.find_EOF() #TODO remove or replace with direct seek(0,2)
        self.file.seek(0)

    
    def read_cell(self):
        """Reads the unit cell from the file.
        """
        self.read_till("Unit Cell")
        
        self.move(2)
        mat = self.read_matrix()
        cell = mat[:, :3]
        return cell

    def read_till(self, string):
        """Reads the file line by line until the condition is found.
        """
        while (line := self.file.readline()) and (re.fullmatch(string, line.strip()) is None):
            pass
        return
            
        
    def read_till_repeat(self, string):
        """Reads the file line by line until the condition is found.
        """
        while (line := self.file.readline()) and (re.fullmatch(f"{string}{{{len(line.strip())}}}", line.strip()) is None):
            pass
        return
            
    def move(self, n: int):
        """Moves the file pointer n lines forward.
        """
        for _ in range(n):
            self.file.readline()
    
    def read_positions(self):
        """Reads the positions from the file.
        """
        
        # find the positions
        self.read_till("Cell Contents")
        self.read_till_repeat('x')
        self.move(4)
        
        if self.check_EOF(): #TODO
            raise EOFError

        positions = []
        symbols = []

        while (line := self.file.readline()) and (re.fullmatch("x+", line.strip()) is None):
            words = line.split()
            symbols.append(words[1])
            positions.append([float(x) for x in words[3:6]])
        
        self.move(1)

        return positions, symbols
    
    def read_forces(self):
        """Reads the forces from the file.
        """

        # find the forces
        self.read_till_forces()
        self.move(5)
        
        forces = []
        
        while (line := self.file.readline()) and (re.fullmatch("\s*\*\s+\*\s*", line) is None):
            forces.append([float(x) for x in line.split()[3:6]])

        self.move(2)
        
        return forces
    
    def read_till_forces(self):
        """Reads the file line by line until forces are found.
        """

        while (line := self.file.readline()) and \
            (re.fullmatch("\*+ Forces \*+", line.strip()) is None):
            pass
        return

    def write(self, frame):
        return NotImplementedError
    
    def fill_atom(self, frame, forces, i, name):
        return NotImplementedError

    def find_EOF(self):
        return NotImplementedError
    
    def check_EOF(self):
        return self.file.tell() >= self.file_size


class Castep_MD_Convertor(Castep_Convertor):
    """Class for reading of Castep MD output files.
    Parameters: 
        file: file objected opened for reading
        max_iter (int): how long to keep looping through a file with unexpected outcome
            before ending the code. 
    """

    def __init__(
            self, 
            file: str,
            finite_set_correction: bool = False):
        
        super(Castep_MD_Convertor, self).__init__(file)

    def read(self, pbc: bool = True) -> list:
        """Reads the file and returns a list of ase.Atoms objects.
        TODO check if position of count_iterations() call affects output
        TODO decide the loop condition
        TODO handle file ending in index error loop instead of with explicit EOFError
        """
        traj = []
        cell = self.read_cell()
        count = self.count_iterations() + 1 #NOTE +1 to include initial configuration before MD

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

            except (IndexError, EOFError) as err: #TODO
                if type(err) is IndexError:
                    while (line := self.file.readline()) and \
                     (re.search("Starting MD iteration", line) is None):
                        pass

                    continue
                
                elif type(err) is EOFError:
                    break
          
        return traj

    def read_energy(self):
        """Reads the energy from the file.
        """
        # find the energy
        self.read_till_repeat('x')
        self.move(4)

        # read the energy
        energy = float(self.file.readline().split()[3])
        self.read_till_repeat('x')
        self.move(1)
        return energy
    
    def find_EOF(self):
        """Find the end of the file.
        """
        # pattern = re.compile("finished MD iteration")
        # i = 0
        # while (line := self.file.readline()):
        #     if pattern.search(line) is not None:
        #         i = self.file.tell()
        # return i
        return self.file.seek(0,2)
    
    def count_iterations(self) -> int:
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
        max_iter (int): how long to keep looping through a file with unexpected outcome
            before ending the code. 
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

    def find_EOF(self):
        return self.file.seek(0, 2)