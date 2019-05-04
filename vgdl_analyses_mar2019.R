library(cowplot)
library("ggplot2")
library("zoom")
library("stats")
library(plyr)
library("dplyr")
library("colorspace")
library("RColorBrewer")
library(purrr)
library(zoo)
library(EnvStats)
library(grid)

## everything starting mar23 has no 15-loss cutoff.
## nov28 old planner-lesion data
## mar28: 10 runs of EMPA with no limit on losses.
## mar30: unclear
## apr4: e-greedy and random policy, both 10x. Random policy incomplete (got kicked off om2)
EMPA_dates = list('mar28', 'apr4')
dqn_path = '~/Projects/atari/vgdl/dqn_data/'
humandatapaths = list.files("~/Projects/atari/vgdl/humandata")

### Toggle the below line to alter what you're reading in
data_to_load = 'EMPA'
data_to_load = 'human'
data_to_load = 'DDQN'

if (data_to_load == 'EMPA'){
  dates_or_groups = EMPA_dates
}else if (data_to_load == 'human'){
  dates_or_groups = groups
}else if (data_to_load == 'DDQN'){
  dates_or_groups = NA #doesn't matter
}

EMPAdata = load_reward_data('EMPA', dates_or_groups)
EMPA_variants = filter(EMPAdata, agent_type!='EMPA')
humandata = load_reward_data('human', dates_or_groups)
dqndata = load_reward_data('DDQN', dates_or_groups)
planner_lesions = load_reward_data('EMPA', dates_or_groups)

alldata = rbind(EMPAdata, humandata, dqndata)
saved_human_normed_data = human_normed_data
human_normed_data = make_human_normed_data(alldata)

zelda_data = filter(EMPA_variants, agent_type=='e-greedy .1', game_name=='zelda')
for (subject in unique(zelda_data$subject_ID)){
  print (c(subject, max(filter(zelda_data, subject_ID==subject)$level_number)))
}

colors = c('steelblue1',
           'purple2', #'mediumorchid2',
           'firebrick2',# 'seagreen3','darkolivegreen1',
           'palegreen3',# 'tomato2', 'salmon', 
           'gray50', 'gray52', 'gray54',
           'goldenrod1', 'goldenrod3', 'darkslategray2', 'goldenrod2', 'darkolivegreen3')
           )
           # 'darkslategray3', 'darkslategray2', 'darkslategray1')#, 'mediumpurple2', 'aquamarine3', 'coral3')
names(colors)=unique(alldata$agent_type)



## density plot summary plot of overall results -- easy to look at.
# (agent_type%in%c('EMPA','no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW', 'no subgoals + no gradient + no IW')
tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
human_normed_data = transform(human_normed_data, agent_type=factor(agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 
                                                                                     'no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                                                                                     'no IW', 'no subgoals + no gradient + no IW',
                                                                                     'DDQN 1k', 'DDQN 10k', 'DDQN 100k', 'random policy')))
human_normed_data$model_cluster = NA
human_normed_data[human_normed_data$agent_type=='EMPA',]$model_cluster = 'EMPA'
human_normed_data[human_normed_data$agent_type%in%c('e-greedy .1'),]$model_cluster = 'exploration lesions'
human_normed_data[human_normed_data$agent_type%in%c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                                                    'no IW', 'no subgoals + no gradient + no IW'),]$model_cluster = 'planner lesions'
human_normed_data[human_normed_data$agent_type%in%c('DDQN 1k', 'DDQN 10k', 'DDQN 100k'),]$model_cluster = 'DDQN'
human_normed_data = transform(human_normed_data, model_cluster=factor(model_cluster, levels=c('EMPA', 'exploration lesions', 'planner lesions', 'DDQN', NA)))

### Stacked plot; each model type gets one row
p = ggplot(filter(human_normed_data, !agent_type%in%c('human', 'random policy')), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.4)+facet_wrap(~agent_type, ncol=1)
p # 12x10

### Stacked and organized by lesion type
p = ggplot(filter(human_normed_data, !agent_type%in%c('human', 'random policy')), aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed performance") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.4)+facet_wrap(~model_cluster, ncol=1)
p # 8x10


## one plot per game summary plot of overall results -- easy to look at.
p = ggplot(subset(human_normed_data), aes(x=agent_type, y=level_percentage, fill=factor(agent_type))) +
  geom_bar(position='dodge', stat='identity')+facet_wrap(~game_name)+scale_fill_manual(values=colors)+
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank())+theme(legend.position='bottom')
p
## save as 10x16


p = ggplot(agentdata, aes(x=cumulative_steps, y=cumulative_wins, color=subject_ID))+geom_point()+geom_smooth()
p

## looks like 10 subjects won zelda, the rest did far worse (0,1, or 2 levels). Be careful how you average.
### you first need to generate cumulative wins
###level1-level2 plots
level_win_saved = level_win
level_win_proportions = level_win
d = filter(alldata, agent_type%in%c('human', 'EMPA', 'DDQN 100k', 'e-greedy .1'))

make_level_win_data = function(d){
  level_win = data.frame(agent_type=as.character(), subject_ID=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            subject_steps_to_win = level_steps
            # subject_steps_to_win = 1
          }
          else{
            subject_steps_to_win = no_win_equivalent_steps
            # subject_steps_to_win = 0
          }
          row = data.frame(agent_type=agent, subject_ID=subject, game_name=game, level_num=l, steps=subject_steps_to_win)
          level_win=rbind(level_win, row)
        }
      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}


make_level_win_proportions = function(d){
  level_win = data.frame(agent_type=as.character(), game_name=as.character(), level_num=as.numeric(), steps=as.numeric())
  levels_to_try=c(1,2,3,4,5)
  no_win_equivalent_steps = 10e6
  for (game in unique(d$game_name)){
    s=filter(d, game_name==game&(level_number%in%levels_to_try|level%in%levels_to_try))
    for (agent in unique(s$agent_type)){
      agentdata = filter(s, agent_type==agent)

      across_subjects = c()
      for (subject in unique(agentdata$subject_ID)){
        prev_cumulative_steps = 0
        subjectdata = filter(agentdata, subject_ID==subject)
        subject_steps_to_win = c()
        for (l in levels_to_try){
          if (l %in% subjectdata$cumulative_wins){
            cumul_steps = min(subjectdata[which(subjectdata$cumulative_wins==l),]$cumulative_steps)
            level_steps = cumul_steps - prev_cumulative_steps
            prev_cumulative_steps = cumul_steps
            # subject_steps_to_win = c(subject_steps_to_win, level_steps)
            subject_steps_to_win = c(subject_steps_to_win, 1)
          }
          else{
            # subject_steps_to_win = c(subject_steps_to_win, no_win_equivalent_steps)
            subject_steps_to_win = c(subject_steps_to_win, 0)

          }
        }
        across_subjects = rbind(across_subjects, subject_steps_to_win)
      }
      across_subjects  = colMeans(across_subjects)
      for (l in levels_to_try){
        row = data.frame(agent_type=agent, game_name=game, level_num=l, steps=across_subjects[l])
        level_win=rbind(level_win, row)

      }
    }
  }
  level_win = transform(level_win, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy .1', "DDQN 100k"))) ## so that columns of plot are reordered
  return(level_win)
}

level_win_proportions = make_level_win_proportions(d)

##Plot of steps to win level 1, conditioned on winning level 0. Only for games where the model *did* win level 1.
##Only the DDQN failed to win level 1
tmpcolors = c('palegreen3','steelblue3','slateblue2','grey50')
names(tmpcolors) = c('human', 'EMPA','e-greedy .1', 'DDQN 100k')

# p = ggplot(subset(level_win, level_num==1&steps!=-Inf), aes(x=short_agent_type, y=log(steps,10), fill=short_agent_type))
# p=p+geom_bar(position='dodge', stat='summary', fun.y='mean')+theme(legend.position='none')+scale_fill_manual(values=colors)
# p


# level_win_no_inf[level_win_no_inf$steps==10e15,]$steps=10e8

tickmarks = c(1,10e0,10e1,10e2,10e3,10e4,10e5,10e6,10e7,10e8,10e9,10e10,10e11,10e12,10e13,10e14,10e15)
logtickmarks=(log(tickmarks,10))

level_win = transform(level_win, agent_type=factor(agent_type, levels=c('human', 'EMPA', 'e-greedy .1', 'DDQN 100k')))

## all levels
p = ggplot(level_win, aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p


## levels 1, 2
p = ggplot(filter(level_win_old, level_num%in%c(1,2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+scale_color_manual(values=tmpcolors)+
  scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+facet_wrap(~level_num, ncol=1)
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win, level_num%in%c(1)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==1)$steps,10), na.rm=TRUE), linetype=agent_type))+
  
    scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)+
  scale_linetype_manual(values=c(1,2,3,4,5))
p

## Individual plots for steps to level 1, steps to level 2...
p = ggplot(filter(level_win,level_num%in%c(2)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==2)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==2)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==2)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==2)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p

p = ggplot(filter(level_win,level_num%in%c(3)), aes(x=log(steps,10), color=agent_type, fill=agent_type))
p=p+geom_density(alpha=.8, adjust=1/10)+xlab('steps to win level')+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='EMPA', level_num==3)$steps,10), na.rm=TRUE), linetype='l'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='human', level_num==3)$steps,10), na.rm=TRUE), linetype='k'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='e-greedy .1', level_num==3)$steps,10), na.rm=TRUE), linetype='j'))+
  geom_vline(aes(xintercept=median(log(filter(level_win, agent_type=='DDQN 100k', level_num==3)$steps,10), na.rm=TRUE), linetype='i'))+
  
  scale_color_manual(values=tmpcolors)+scale_fill_manual(values=tmpcolors)+scale_x_continuous(breaks=logtickmarks,labels=tickmarks)
p



p = ggplot(level_win_proportions, aes(x=level_num, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='summary',fun.y='mean', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~agent_type, nrow=1)
p=p+ylab('Proportion')+ggtitle('Level completion across games')+xlab("Level number")
p


p = ggplot(level_win_proportions, aes(x=game_name, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
  scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
p=p+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
p


for (game in unique(level_win_proportions$game_name)){
  p = ggplot(filter(level_win_proportions, game_name==game), aes(x=agent_type, y=as.numeric(steps), fill=agent_type))+geom_bar(stat='identity', position='dodge')+
    scale_fill_manual(values=tmpcolors)+facet_wrap(~level_num, ncol=1) #facet_grid(level_num~game_name)#
  p=p+ggtitle(game)+theme(axis.text.x = element_text(angle = 90, hjust = 1))+ylab('Proportion of agents to complete level')
  
  newdir='~/Projects/atari/vgdl/interaction_plots/agent_win_proportions/'
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=4, height=6)
  
}


# complete_games = c()
# overcomplete_games = c()
# for (game in unique(EMPA_data$game_name)){
#   l = length(unique(filter(EMPA_data, game_name==game)$subject_ID))
#   if (l!=10){
#     overcomplete_games = c(overcomplete_games, game)
#   }else{
#     complete_games = c(complete_games, game)
#   }
# }

# for (game in complete_games){
#   p = ggplot(filter(EMPA_data, game_name==game), aes(x=cumulative_timestep, y=cumulative_wins, color=subject_ID))
#   p = p+geom_point()+geom_smooth()
#   # p
#   newdir='~/Projects/atari/vgdl/empa_plots/by_subject/'
#   dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
#   title = paste(newdir, game, '.png', sep='')
#   ggsave(title, plot=p, width=7, height=5) 
# }


p = ggplot(filter(alldata, agent_type%in%c('human', 'EMPA'), game_name=='avoidgeorge'), aes(x=cumulative_steps, y=cumulative_wins, color=agent_type))
p = p+geom_point()+geom_smooth()+scale_color_manual(values=colors)
p


make_human_normed_data = function(dataframe){
  ## make data structure for looking at levels_won for different planner settings (corresponding to runs on different days)
  plantimedata = data.frame(game_name=as.character(), agent_type=as.character(), max_score=as.numeric(), 
                            max_steps=as.numeric(), planning_time=as.numeric(), max_levels_won=as.numeric(),
                            level_num=as.numeric(), level_efficiency=as.numeric())
  
  for (j in 1:length(unique(dataframe$agent_type))){
    agent = unique(dataframe$agent_type)[j]
    print(agent)
    for (i in 1:length(unique(dataframe$game_name))){
      g = subset(dataframe, game_name==unique(dataframe$game_name)[i])
      print(unique(dataframe$game_name)[i])
      s = subset(g, agent_type==agent)
      if (length(s$cumulative_steps)>0){
        ## grab each subject's max_steps and max_wins.
        level_maxes = list()
        cumulative_step_maxes = list()
        idx=1
        for (k in 1:length(unique(s$subject_ID))){
          subject = unique(s$subject_ID)[k]
          subjectdata = s[which(s$subject_ID==subject),]
          if (length(subjectdata$cumulative_steps)>0){
            if(max(subjectdata$cumulative_steps)>0){
              level_maxes[[idx]] = max(subjectdata$cumulative_wins)
              cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
              idx = idx+1            
            }
            
          }
        }
        
        ## mean vector of win numbers
        mean_wins = mean(as.numeric(as.vector(level_maxes)))
        
        ##mean of vector steps-to-win ratios
        l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
        
        ## the row we want
        r = subset(s, cumulative_steps==max(cumulative_steps))[1,]
        ## take only the relevant columns and put them in the new data frame
        new = data.frame(game_name=r$game_name, agent_type=r$agent_type, max_score=r$score, 
                         max_steps=r$cumulative_steps, mean_levels_won=mean_wins,
                         level_num=subset(games_to_levels, (game_name==r$game_name))$num_levels,
                         level_efficiency=l_e)
        plantimedata = rbind(plantimedata, new)
      }
    }
  }
  
  
  plantimedata = mutate(plantimedata, level_percentage=mean_levels_won/level_num)
  plantimedata = mutate(plantimedata, composite_ratio = level_percentage*level_efficiency)
  
  plantimedata$human_normed_composite_ratio=NA
  ##norm by human level_efficiency
  for (i in 1:length(unique(plantimedata$game_name))){
    game = unique(plantimedata$game_name)[i]
    human_composite_ratio = subset(plantimedata, agent_type=='human' & game_name==game)$composite_ratio
    for (agent in unique(plantimedata$agent_type)){
      row = plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]
      plantimedata[which(plantimedata$agent_type==agent & plantimedata$game_name==game),]$human_normed_composite_ratio = row$composite_ratio/human_composite_ratio
    }
  }
  
  for (i in 1:length(plantimedata$human_normed_composite_ratio)){
    if (plantimedata$human_normed_composite_ratio[i]==0){
      plantimedata$human_normed_composite_ratio[i]=10e-8
    }
  }
  return(plantimedata)
  }

load_reward_data = function(data_to_load, dates_or_groups){
    if (data_to_load=='EMPA'){
      data = c()
      for (date in dates_or_groups){
      path = paste('~/Projects/atari/vgdl/',date, '/csv_data/merged_data', sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      
      # if ('exploration_burn_ins' %in% names(d)){
      #   d$exploration_burn_ins = as.numeric(d$exploration_burn_ins) ## you might want to make this as.numeric()
      # }else{
      #   d$exploration_burn_ins = NA
      # }
      
      if(length(data)==0){
        data = d
      }
      else{
        for(colname in names(d)){
          if (!(colname %in% names(data))){
            data[,colname] = NA
          }
        }
        for(colname in names(data)){
          if(!(colname %in% names(d))){
            d[,colname]=NA
          }
        }
        data = rbind(data,d)
      }
      }
      data$modelrun_ID = as.factor(data$modelrun_ID)
      data$cumulative_steps = as.numeric(as.character(data$cumulative_timestep))
      data$long_agent_type = as.factor(data$agent_type)
      e_greedy_05='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1a='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=1000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      e_greedy_1b='IW=1_rand=False_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=True_egv=N_fe=0.1_sTE=2000_hyb=False_nnon=55_ontl=1000_oltl=1000_sD=5_lhol=2_igl=FR'
      planner_AGH1='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH1_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH2='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH2_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_AGH3='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IW='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      planner_IW_AGH3='IW=2_eaa=True_ea=True_sh=500_lh=1000_sha=1.05_lha=2.0_shr=[200, 500, 1000]_nF=True_abmax=50000_lR=True_eG=False_sTE=1000_hyb=False_PL=IW-AGH3_nnon=55_ontl=1000_oltl=1000_sD=3_lhol=2_igl=FR'
      data$agent_type = NA
      if (e_greedy_1a %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1a,]$agent_type = 'e-greedy .1'
      }
      if (e_greedy_1b %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_1b,]$agent_type = 'e-greedy .1'
        
      }
      if (e_greedy_05 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==e_greedy_05,]$agent_type = 'e-greedy .05'
      }
      if (planner_AGH1 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH1,]$agent_type = 'no goal gradient'
      }
      if (planner_AGH2 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH2,]$agent_type = 'no subgoals'
      }
      if (planner_AGH3 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_AGH3,]$agent_type = 'no subgoals + no gradient'
      }
      if (planner_IW %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IW,]$agent_type = 'no IW'
      }
      if (planner_IW_AGH3 %in% unique(data$long_agent_type)){
        data[data$long_agent_type==planner_IW_AGH3,]$agent_type = 'no subgoals + no gradient + no IW'
      }
      for (agent in unique(data$long_agent_type)){
        if (grepl('rand=True', agent)){
          data[grepl('rand=True', data$long_agent_type),]$agent_type = 'random policy'
        }
      }
      if (NA %in% unique(data$agent_type)){
        data[is.na(data$agent_type),]$agent_type = 'EMPA'
      }
      
      data$score = as.numeric(as.character(data$sparse_score))
      data = select(data, -timestep, -level_max_score, -cumulative_max_score, -sparse_score, -level_accumulated_score, 
                    -episode_end, -win, -planner_nodes, -planner_settings, -cumulative_planner_nodes, 
                    -cumulative_timestep, condition, -exploration_burn_ins)
      if ('entropy'%in% names(data)){
        data = select(data, -entropy)
      }
      if ('time_elapsed'%in%names(data)){
        data = select(data, -time_elapsed)
      }
      if ('sparse_levels_won'%in%names(data)){
        data = select(data, -sparse_levels_won)
      }
      data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }else if (data_to_load == 'DDQN'){
    dqndata = list()
    for (gamefile in list.files(dqn_path)){
      filename = paste(dqn_path,gamefile,sep='')
      if(grepl('dqn/', filename)){
        gamenamestart = unlist(gregexpr('dqn/',filename))+nchar('dqn/')
        gamenameend = unlist(gregexpr('_reward', filename))-1        
      }else if (grepl('dqn_data/', filename)){
        gamenamestart = unlist(gregexpr('dqn_data/',filename))+nchar('dqn_data/')
        gamenameend = unlist(gregexpr('_DDQN_reward', filename))-1  
      }

      game = substr(filename, gamenamestart, gamenameend)
      if (grepl('k_', filename)){
        subject_ID_start = unlist(gregexpr('k_',filename))+2
        subject_ID_end = unlist(gregexpr('.csv', filename))-1
        subject_ID = substr(filename, subject_ID_start, subject_ID_end)
      }else{
        subject_ID = create_rand_string()
      }
      d=read.csv(filename, header=TRUE, na.strings='NA')
      
      d$score = d$ep_reward
      d$game_name = as.factor(remove_string_from_name(game))
      d$cumulative_steps = d$steps
      d$subject_ID = as.factor(subject_ID)
      
      if ((grepl('101', filename) || grepl('trial1', filename) || grepl('decay1k', filename))){
        d$agent_type = as.factor("DDQN 1k") ## refers to the eps_decay (epsilon-greedy annealing) parameter in the DDQN implementation. 
      }else if ((grepl('102', filename)|| grepl('trial2', filename) || grepl('decay10k', filename))){
        d$agent_type = as.factor("DDQN 10k")
      }else if ((grepl('103', filename)||grepl('trial3', filename) || grepl('decay100k', filename))){
        d$agent_type = as.factor("DDQN 100k")
      }else{
        d$agent_type = as.factor("DDQN")
      }
      d$long_agent_type = d$agent_type
      d$cumulative_wins = as.numeric(0)
      for (i in 2:length(d$level)){
        if (d$level[i]>d$level[i-1]){
          d$cumulative_wins[i] = d$cumulative_wins[i-1]+1
          # d$sparse_levels_won[i] = d$cumulative_wins[i]
        }
        else{
          d$cumulative_wins[i] = d$cumulative_wins[i-1]
        }
      }
      d$level_number = d$level
      
      dqndata = rbind(dqndata,d)
    }
    data = dqndata
    data$modelrun_ID = NA
    data = select(data, -criteria, -level, -ep_reward)
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
    
  }else if (data_to_load == 'human'){
    humandata = list()
    for (humandatapath in humandatapaths){
      path = paste('~/Projects/atari/vgdl/humandata/',humandatapath, sep='')
      d=read.csv(path, header=TRUE, na.strings='NA')
      if (length(humandata)==0){
        humandata = d
      }
      else{
        humandata = rbind(humandata,d)
      }
    }
    humandata$long_agent_type=as.factor('human')
    humandata$agent_type=as.factor('human')
    humandata$modelrun_ID = as.factor('oct29')
    humandata$condition = as.factor('full')
    
    humandata$game_name = as.factor(humandata$game_name)
    humandata = select(humandata, -levels_lost, -group, -gameNumber, -gameRound)
    data = humandata
    data = data[c('game_name',  'agent_type', 'long_agent_type', 'subject_ID', 'modelrun_ID', 'level_number', 'cumulative_steps', 'cumulative_wins', 'score')]
  }
  
  data$game_name = as.factor(as.character(lapply(as.vector(data$game_name), remove_string_from_name)))
  return (data)
}

create_rand_string <- function() {
  a <- do.call(paste0, replicate(1, sample(LETTERS, 1, TRUE), FALSE))
  paste0(a, sprintf("%04d", sample(9999, 1, TRUE)), sample(LETTERS, 1, TRUE))
}



game_names = c(levels(data$game_name))
