import pandas as pd
import math
# import scipy  
# import seaborn as sns;sns.set(style="white")


class Hurestic_Dimensioning:
    """
    Model to calculate the cell radius and power allocation on the cell edge throughput per service

    """

    def __init__(self,path_to_csv,p2,p3,a,b,cell_load,w_x_thr,zeta,radius) -> None:
        """
        Args:
            path_to_csv (str): Path to the csv file
            p2 (int):          probability of active devices(rrc_inactive)
            p3 (int):          probability of active devices(rrc_connected)
            a (int):           Lower range of samples
            b (int):           Upper range of samples
            cell_load (int):   Cell Load
            w_x_thr (int):     threshold number of devices per gNB
            zeta (int):        MNO’s requirements. 
            radius (int):      Radius of the deployment area
        """
        self.path_to_csv = path_to_csv
        self.p2 = p2
        self.p3 = p3
        self.a = a
        self.b = b
        self.cell_load = cell_load
        self.w_x_thr = w_x_thr
        self.zeta = zeta
        self.radius = radius
        self.transit_df = pd.DataFrame({"mu":[0,1,2],
                           "delta_f":[15,30,60],
                           "n_mu_slot":[1,2,4],
                           "t_slot":[1, 0.5, 0.25],
                           "v_layers":[4,4,2],
                           "Qm":[8,8,6],
                           "Nrb":[160, 24, 11],
                           "r_x":[100, 15, 7]})

    def network_acquisition(self,df, a, b):

        """
            Removes CID's having samples lesser or higher than the input range (a,b)

            Args:
                m (dataframe):  Data containing top 3 MNC's by sample
                a (int):        Lower range of samples
                b (int):        Upper range of samples 
            
            Returns:
                Returns a dataframe after removing CID's having samples lesser or higher 
                than the input range (a,b) from the top 3 MNC's

        """
        
        df1 = pd.DataFrame()
        for mnc in df["MNC"].unique().tolist():
            m = df[df["MNC"]==mnc]
            

            m = m[ (m["samples"]<b)  & (m["samples"]>a)]
            
            if m.shape[0]==0:
                # print(f"For MNC: {mnc}, no data present in range ({a},{b})")
                pass

            else:
                # find LAC id having max samples
                hm_lac = m.groupby(["LAC"], as_index=False)["samples"].sum().sort_values("samples", ascending=False)["LAC"].values[0]


                data = m[m["LAC"]==hm_lac]

                # print(data)
                # print("MNC:",mnc)
                # print("LAC:", hm_lac)
                # print("CID:",data.loc[data["samples"].idxmax(), 'CID'])

                # df1 = pd.concat([df1, data.sort_values("samples", ascending = False)]).reset_index(drop=True)
                df1 = pd.concat([df1, data.sort_values("samples", ascending = False)])

                # print("CID's:", data.sort_values("CID", ascending = False) )

            # print()

        return(df1)

    def transmission_model(self,mu, OH):

        """
            Calculate Maximum Transmission Rate per service

            Args:
                mu (int):   Represent the three services (0,1,2)
                OH (float): Over Head value based on the Direction of data transfer, 
                            Uplink or Downlink 
            
            Returns: 
                Maximum Transmission Rate

        """

        transit_df = self.transit_df

        # Rmax (if you don't know what is it, don't change). Value depends on the type of coding from 3GPP 38.212 and 3GPP 38.214 
        # (For LDPC code maximum number is 948/1024 = 0.92578125)
        R_max = 948/1024

        # Scaling Factor 
        f = 1

        # Tμs(j) = (10^-3)/(14*2^μ) – average OFDM symbol duration in a subframe for μ(i) value for normal cyclic prefix
        t_s_mu = 10**-3/(14* (2**mu))

        # Maximum number of MIMO layers ,3GPP 38.802: maximum 8 in DL, maximum 4 in UL
        v_layers = transit_df[transit_df["mu"]==mu]["v_layers"].values[0]

        # Modulation order (QPSK-2, 16QAM-4, 64QAM-6, 256QAM-8)
        Qm = transit_df[transit_df["mu"]==mu]["Qm"].values[0]

        V = v_layers * Qm * f * R_max

        # The maximum resource block allocation per service x is NRB
        Nrb = transit_df[transit_df["mu"]==mu]["Nrb"].values[0]

        # Max Transmission Rate
        psi = 10**-6 * ( ( (V * Nrb * 12)/t_s_mu ) * (1 - OH) )

        return(psi)

    def coverage_computation(self,fitered_data, p_tx, mu):


        """
            Calculate Cell Radius and power allocation on the cell edge throughput per service

            Args:
                fitered_data (dataframe): Dataframe of top 3 MNC by sample
                p_tx (int)              : Transmit Power per gNB. 
                mu   (int)              : Represent the three services (0,1,2)

            Return:
                R_cov                   : Cell Radius
                E_x_cet_range           : power allocation on the cell edge throughput
        """

        transit_df = self.transit_df


        # number of total resource block
        N_thr_RB = transit_df["Nrb"].sum()

        # Number fo sub carriers in the resource block
        N_SC = 12

        #  shadowing factor
        sigma = 5

        h_g_NB = 10 # antenna height
        h_UE = 12.5 # (assumed)  user height

        
        lamda = (30 * 10**9) / 299792458

        d_bp = (4*math.pi*h_g_NB*h_UE)/lamda #breakpoint distance 



        # total number of physical resource block
        N_x_RB = transit_df[transit_df["mu"]==mu]["Nrb"].values[0]

        # The power available for service x
        P_x_tx = p_tx - 10 * math.log10( (N_x_RB/N_thr_RB) )

        # total number of sub carriers per x
        Nx = N_x_RB * N_SC
        
        # effective power per sub carrier
        E_x = P_x_tx - 10 * math.log10(Nx)

        # number of PRBs to provide CET
        N_x_cet_range = N_x_RB /(.95 * fitered_data["samples"])

        # power associated with the sub-carriers of these PRBs  
        E_x_cet_range = [E_x + 10 * math.log10(N_x_cet * N_SC) for N_x_cet in N_x_cet_range]

        
        # assumed cell load
        delta_cov = 0

        # sum of all the losses during propagation 
        L = -10 * math.log10(1-delta_cov)

        # PL_x_max determines the maximum cell range of a gNB
        PL_x_max_range =  [E_x_cet - L for E_x_cet in E_x_cet_range]


        # Coverage cell range 
        R_cov = [ 10 ** ((PL_max - ( 32.4  + 20 * math.log10(fc) - 9.5 *math.log10( (d_bp)**2 + (h_g_NB - h_UE)**2 ) + sigma))/40)  for PL_max, fc in zip(PL_x_max_range, fitered_data["MNC"]) ] 

        return(R_cov, E_x_cet_range)

    def capacity_model(self,W_x_thr, zeta, mu, p2, p3):

        """
            Calculate the threshold number of devices per gNB based on MNO’s requirements.

            Args: 
                W_x_thr: threshold number of devices per gNB
                zeta   : MNO’s requirements. 
                mu     : Represent the three services (0,1,2)
                p(p2+p3): Probability of active devices, also refers to the cell load,
                        as it corresponds to the percentage of active devices

            Returns:
                result : The threshold number of devices per gNB based on MNO’s requirements
        """

        transit_df = self.transit_df


        # probability of active devices
        p = p2 + p3

        # probability of non-active devices
        p1 = 1-p
        

        P_k_ls=[]
        r_circum_x_W_x_ls = []


        # data rate
        r_x = transit_df[transit_df["mu"]==mu]["r_x"].values[0]

        # the maximum number of active devices to provide rx in the given transmission bandwidth, DL in our case 
        W_x_max = math.floor(self.transmission_model(mu, OH= 0.08)/r_x)
        # print(W_x_max)


        result = 0

        for W_x_k in range(W_x_max,W_x_thr+1, 1):
            # eq 9
            P_k = (math.factorial(W_x_thr)/( math.factorial(W_x_k) *  math.factorial(W_x_thr-W_x_k))) * (p2+p3)**W_x_k * (p1)**(W_x_thr-W_x_k)
            P_k_ls.append(P_k)


            # eq 10
            # the DL transmission rate, 
            # We choose the DL as the representative case, compared to the UL, as significantly larger data rates are generaly required for DL applications
            tr_DL = self.transmission_model(mu, OH= 0.08)/W_x_k
            # print(tr_DL)

            # the data rate transmitted per device for service x, which depends on Wx at a given time instant
            r_circum_x_W_x = min([tr_DL , r_x])
            r_circum_x_W_x_ls.append(r_circum_x_W_x)

            # eq 12
            # The average expected data rate
            E_r_circum_x = sum([p_k * r_circum_x_w_x  for p_k, r_circum_x_w_x in zip(P_k_ls, r_circum_x_W_x_ls) ])


            # eq 13, the average number of active devices
            E_W_x = p * W_x_thr


            # eq 14
            prob = sum([ (math.factorial(W_x_k)/( math.factorial(k) *  math.factorial(W_x_k-k))) * (p2+p3)**k * (p1)**(W_x_k-k)   for k in range(0,W_x_max+1)])

            if prob >= zeta:
                result = W_x_k
                # break
        
        return(result)


    def NetDimensioning(self,Agm, m_list,δcov,phim,top_3_mnc_samples,m_data):

        """
            Args:
                Agm              : High Traffic Concentraion area at min and max power
                m_list           : Top 3 MNC by sample
                δcov             : Assumed cell load
                phim             : 
                top_3_mnc_samples:
                m_data           : Dataframe of the top 3 MNC


            Returns:
                Zcov             : The cell range R(in km).
                Zcap             : The minimun number of radio sites Z
                Ptx              : Transmit power level Ptx

        """

        mu_ls = [0,1,2]

        fitered_data = self.network_acquisition(m_data, self.a, self.b)

        results = []
        W_x_thr = self.w_x_thr

        zeta = self.zeta

        p2 = self.p2
        p3 = self.p3

        s = 3
        β = 0
        for mu in mu_ls:
            Wthr_x = self.capacity_model( W_x_thr, zeta, mu, p2, p3)
            β += Wthr_x
        β = β*s
        R_x_cov = [0] * 20
        
        for m_idx in m_list:
            for x_idx in [1,2,3]:
                for Ptx_variable in range(0, 10 + 1):
                    Ecet,r_cov = self.coverage_computation(fitered_data, Ptx_variable, x_idx-1)
                    Ecet_x = Ecet[x_idx]
                    R_x_cov[m_idx] = r_cov[x_idx]
            k = R_x_cov.index(min(R_x_cov))
            Rcov = R_x_cov[k]
            # δmin = int(top_3_mnc_samples[0])
            # δmax = int(top_3_mnc_samples[- 1])
            Zcov = [math.inf] * 100
            Zcap = [math.inf] * 100
            for δcap in range(1, 100 + 1):
                Ac = β * δcap / phim[m_idx]
                Rcap = (Ac / Agm)**0.5
                diff_R = abs(Rcov - Rcap)
                diff_L = abs(δcov - δcap)
                try:
                    if diff_L <= 1 and diff_R <= 10:
                        Zcov[δcap] = Agm / (1.95 * Rcov**2)
                        Zcap[δcap] = Agm / Ac
                except:
                    pass
            z = min(enumerate(zip(Zcov, Zcap)), key=lambda x: x[1])[0]
            Ptx = list(range(0, 10 + 1))
            results.append((Zcov[z], Zcap[z], Ptx[z]))
        return(results)


    def calculate_results(self):


        col_names = ["Radio", "MCC", "MNC", "LAC", "CID", "Unit", "long", "lat", "radius", "samples", "changeble", "created", "updated", "Average_Signals"]
        df = pd.read_csv(self.path_to_csv, names = col_names)

        result = df.groupby(['MNC'])['samples'].sum()
        result.sort_values(ascending=False,inplace=True)

        # store top 3 MNCs in a list
        top_3_mnc = result.index[:3].tolist()
        top_3_mnc_samples = result.values[:3].tolist()

        phi_m = {}
        for i in range(len(top_3_mnc)):
            x = top_3_mnc_samples[i]
            y = x/(1000*1000*math.pi)
            phi_m[top_3_mnc[i]] = y



        m_data = df[df['MNC'].isin(top_3_mnc)]


        Agm =  math.pi*self.radius**2

        m_list = top_3_mnc
        δcov = self.cell_load
        phim = phi_m

        output = self.NetDimensioning(Agm, m_list,δcov,phim,top_3_mnc_samples,m_data)
        

        return(output)






