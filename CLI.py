import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BAWFilterDesigner:
    def __init__(self):
        self.resonators = {}  # Dictionary to store resonators
        self.resonator_count = 0  # Unique counter for resonator IDs
        self.filter_response = None


    def import_csv(self, file_path):
        try:
            # Read the .csv file, skip metadata
            data = pd.read_csv(file_path, comment='%')
            data.columns = ['Frequency', 'Admittance']

            # Add a new resonator with a unique ID
            self.resonator_count += 1
            resonator_id = f"Resonator_{self.resonator_count}"
            self.resonators[resonator_id] = (data['Frequency'].values, data['Admittance'].values)

            print(f"{resonator_id} imported successfully from {file_path}.")

        except Exception as e:
            print(f"Error importing file: {e}")

    def list_resonators(self):
        if not self.resonators:
            print("No resonators imported.")
        else:
            print("Imported Resonators:")
            for resonator_id in self.resonators.keys():
                print(f"- {resonator_id}")

    def design_ladder_filter(self):
        if len(self.resonators) < 2:
            print("At least two resonators are required for a ladder filter.")
            return
        self.filter_response = self._cascade_ladder()
        print("Ladder filter designed successfully!")

    def design_lattice_filter(self):
        if len(self.resonators) < 2:
            print("At least two resonators are required for a lattice filter.")
            return
        self.filter_response = self._cascade_lattice()
        print("Lattice filter designed successfully!")

    def _cascade_ladder(self):
        # Combine resonators in a ladder configuration
        total_admittance = None
        for i, (name, (frequencies, admittance)) in enumerate(self.resonators.items()):
            if total_admittance is None:
                total_admittance = admittance
            else:
                if i % 2 == 0:  # Parallel
                    total_admittance += admittance
                else:  # Series
                    total_admittance = 1 / (1 / total_admittance + 1 / admittance)
        return total_admittance

    def _cascade_lattice(self):
        # Combine resonators in a lattice configuration
        names = list(self.resonators.keys())
        f1, y1 = self.resonators[names[0]]
        f2, y2 = self.resonators[names[1]]
        lattice_admittance = (y1 * y2) / (y1 + y2)
        return lattice_admittance

    def save_results(self, output_file):
        if self.filter_response is None:
            print("No filter response to save.")
        else:
            frequencies = next(iter(self.resonators.values()))[0]
            response_data = pd.DataFrame({
                'Frequency': frequencies,
                'Combined Admittance': self.filter_response
            })
            response_data.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}.")

    def plot_combined_admittance(self):
        if self.filter_response is None:
            print("No filter response to plot.")
        else:
            frequencies = next(iter(self.resonators.values()))[0]
            plt.plot(frequencies, np.abs(self.filter_response), label="Admittance |Y(f)|")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Admittance (S)')
            plt.title('Combined Admittance Response')
            plt.grid()
            plt.legend()
            plt.show()

    def plot_s_parameters(self, z0=50):
        if self.filter_response is None:
            print("No filter response to compute S-parameters.")
        else:
            frequencies = next(iter(self.resonators.values()))[0]
            z_combined = 1 / self.filter_response
            #s11 = (z_combined - z0) / (z_combined + z0)
            s11 = np.log10(np.abs(1/(self.filter_response)))
            plt.plot(frequencies, s11, label="|S11| (dB)")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('S11 (dB)')
            plt.title('S11 Parameter')
            plt.grid()
            plt.legend()
            plt.show()

    def compute_quality_factor(self):
        if self.filter_response is None:
            print("No filter response to compute Q-factor.")
        else:
            frequencies = next(iter(self.resonators.values()))[0]
            admittance = np.abs(self.filter_response)
            peak_index = np.argmax(admittance)
            f_res = frequencies[peak_index]

            # Compute bandwidth around -3dB from the peak
            half_power_point = admittance[peak_index] / np.sqrt(2)
            lower_f = frequencies[np.where(admittance[:peak_index] < half_power_point)[-1][-1]]
            upper_f = frequencies[np.where(admittance[peak_index:] < half_power_point)[0][0] + peak_index]
            bandwidth = upper_f - lower_f

            q_factor = f_res / bandwidth
            print(f"Resonant Frequency: {f_res} Hz")
            print(f"Bandwidth: {bandwidth} Hz")
            print(f"Quality Factor (Q): {q_factor:.2f}")

            return f_res, bandwidth, q_factor

    def plot_response(self):
        self.plot_combined_admittance()
        self.plot_s_parameters()
        self.compute_quality_factor()


def main():
    designer = BAWFilterDesigner()

    while True:
        print("\nBAW Filter Designer CLI")
        print("======================")
        print("Available commands:")
        print("1. Import COMSOL .csv file")
        print("2. List imported resonators")
        print("3. Design ladder filter")
        print("4. Design lattice filter")
        print("5. Save results")
        print("6. Plot combined filter response")
        print("7. Exit")

        command = input("Enter command number: ")

        if command == "1":
            file_path = input("Enter path to .csv file: ")
            designer.import_csv(file_path)
        elif command == "2":
            designer.list_resonators()
        elif command == "3":
            designer.design_ladder_filter()
        elif command == "4":
            designer.design_lattice_filter()
        elif command == "5":
            output_file = input("Enter output file name (e.g., results.csv): ")
            designer.save_results(output_file)
        elif command == "6":
            designer.plot_response()
        elif command == "7":
            print("Exiting...")
            break
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
