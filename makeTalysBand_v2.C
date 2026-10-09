#include <stdio.h>
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <cstring>
#include <stdlib.h>
#include <math.h>
#include <ctime>
#include <vector>
#include <sstream>
#include <string>
#include <array>
#include <iterator>
// this is version 2.0, which is formatted for files coming out of Artemis' python script for 74Se / 102Pd.
// CHECK / CHANGE EVERY TIME: LINES 19-23, 44, & 107

using namespace std;

void processTalysFiles(string outName) {
    int ldm[] = {1,2,4,5,6};
    int gsf[] = {8,9};
    int gsfM[] = {1,2,3};
    int upbend[] = {0,1}; // 0 = 'n', 1 = 'y'
    int alphaomp[] = {3,4,5,6};

    const int totFiles = (sizeof(ldm) / sizeof(ldm[0])) * 
    		     (sizeof(gsf) / sizeof(gsf[0])) * 
                     (sizeof(gsfM) / sizeof(gsfM[0])) * 
                     (sizeof(upbend) / sizeof(upbend[0])) * 
                     (sizeof(alphaomp) / sizeof(alphaomp[0]));

    cout << "TOTAL NUMBER OF FILES TO PROCESS = " << totFiles << endl;
    
    ofstream outFile(outName);
    char filename[200];
    string line;

    vector<double> x_vals;
    vector<double> csMin;
    vector<double> csMax;

    // -----------------------------
    // Read TALYS data sequentially
    // -----------------------------
    for (int nFile = 0; nFile < totFiles; nFile++) {
        sprintf(filename, "102Pd_astro/i_%i/astrorate.p", nFile); // for calculating the astrorate band
        //sprintf(filename, "all_talys/i_%i/pprod.tot", nFile); // used rp034074.tot for 73As --> 74Se; could also try gprod.tot
        
        ifstream inFile(filename); // Open the file directly
        if (!inFile) {
            cout << "No input file: " << filename << " (skipping)" << endl;
            continue;
        }

        cout << "Processing file " << nFile << " ----" << endl;
        int entryIndex = 0;

        while (getline(inFile, line)) {
            if (line.empty()) continue;
            if (line[0] == '#') continue;

            double current_x, current_y;
            stringstream ss(line);
            
            if (!(ss >> current_x >> current_y)) { 
            	std::cout << "NO DATA TO PARSE for file i_" << nFile << std::endl;
            	continue;
            	}

            if (nFile == 0) {
                // First valid file populates the initial structure
                x_vals.push_back(current_x);
                csMin.push_back(current_y);
                csMax.push_back(current_y);
               // std::cout << "RUNNING for file i_" << nFile << std::endl;
               //std::cout << "file " << nFile << "  entry " << entryIndex << "  x = " << current_x << "  y = " << current_y << endl;
            } else {
                // Check bounds to prevent crashing if a file has extra lines
                if (entryIndex >= x_vals.size()) break; 
                
                if (current_y < csMin[entryIndex]) csMin[entryIndex] = current_y;
                if (current_y > csMax[entryIndex]) csMax[entryIndex] = current_y;
               // std::cout << "RUNNING for file i_" << nFile << std::endl;
               //std::cout << "file " << nFile << "  entry " << entryIndex << "  x = " << current_x << "  y = " << current_y << endl;
            }
            entryIndex++;
        }
        
        inFile.close(); // Automatically closes before moving to next file loop
    }

    // -----------------------------
    // Write output file
    // -----------------------------
    int n = x_vals.size();
    cout << "Writing " << n << " entries to " << outName << endl;
    
    for (int i = 0; i < n; i++) {
        outFile << x_vals[i] << " "
                << csMin[i] << " "
                << csMax[i] << endl;
    }

    outFile.close();
    cout << "Finished writing " << outName << endl;
}

int makeTalysBand_v2()
{
    processTalysFiles("talys_band_102Pdgp_astrorate.dat");
    
    return 0;
}
